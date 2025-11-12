"""
Unit tests for the KeyboardListener module.
"""

import unittest
import json
import os
import tempfile
from unittest.mock import Mock, patch, MagicMock

# Try to import listener - skip tests if dependencies unavailable
try:
    from listener import KeyboardListener, STRATAGEM_ACTIVATION_DELAY, KEY_PRESS_DURATION, KEY_RELEASE_DELAY
    LISTENER_AVAILABLE = True
except (ImportError, Exception):
    LISTENER_AVAILABLE = False


@unittest.skipIf(not LISTENER_AVAILABLE, "Listener dependencies not available")
class TestKeyboardListener(unittest.TestCase):
    """Test cases for KeyboardListener class."""

    def setUp(self):
        """Set up test fixtures."""
        # Create temporary files for testing
        self.test_dir = tempfile.mkdtemp()
        self.stratagems_file = os.path.join(self.test_dir, "test_stratagems.json")
        self.macros_file = os.path.join(self.test_dir, "test_macros.json")

        # Create test data
        self.test_stratagems = {
            "Test Stratagem": ["i", "j", "k", "l"],
            "Mission - Reinforce": ["i", "k", "l", "j", "i"]
        }
        self.test_macros = {
            "insert": "Test Stratagem",
            "home": "Mission - Reinforce"
        }

    def tearDown(self):
        """Clean up test fixtures."""
        # Remove temporary files
        if os.path.exists(self.stratagems_file):
            os.remove(self.stratagems_file)
        if os.path.exists(self.macros_file):
            os.remove(self.macros_file)
        os.rmdir(self.test_dir)

    def test_initialization(self):
        """Test that KeyboardListener initializes correctly."""
        listener = KeyboardListener(self.stratagems_file, self.macros_file)

        self.assertEqual(listener.stratagems_file, self.stratagems_file)
        self.assertEqual(listener.macro_file, self.macros_file)
        self.assertTrue(listener.running)
        self.assertIsNotNone(listener.data_lock)

    def test_load_stratagems_success(self):
        """Test loading stratagems from a valid JSON file."""
        # Write test data to file
        with open(self.stratagems_file, 'w') as f:
            json.dump(self.test_stratagems, f)

        listener = KeyboardListener(self.stratagems_file, self.macros_file)

        self.assertEqual(listener.stratagems, self.test_stratagems)

    def test_load_stratagems_file_not_found(self):
        """Test that default stratagems are generated when file is missing."""
        listener = KeyboardListener(self.stratagems_file, self.macros_file)

        # Should have default stratagems
        self.assertGreater(len(listener.stratagems), 0)
        self.assertIn("Mission - Reinforce", listener.stratagems)

    def test_load_stratagems_invalid_json(self):
        """Test handling of malformed JSON file."""
        # Write invalid JSON to file
        with open(self.stratagems_file, 'w') as f:
            f.write("{ invalid json }")

        listener = KeyboardListener(self.stratagems_file, self.macros_file)

        # Should have default stratagems
        self.assertGreater(len(listener.stratagems), 0)

    def test_load_macros_success(self):
        """Test loading macro bindings from a valid JSON file."""
        # Write test data to file
        with open(self.macros_file, 'w') as f:
            json.dump(self.test_macros, f)

        listener = KeyboardListener(self.stratagems_file, self.macros_file)

        self.assertEqual(listener.bindings, self.test_macros)

    def test_load_macros_file_not_found(self):
        """Test that default macros are generated when file is missing."""
        listener = KeyboardListener(self.stratagems_file, self.macros_file)

        # Should have default bindings
        self.assertGreater(len(listener.bindings), 0)
        self.assertIn("insert", listener.bindings)
        self.assertIn("home", listener.bindings)

    def test_generate_empty_stratagems(self):
        """Test generation of default stratagems."""
        listener = KeyboardListener(self.stratagems_file, self.macros_file)
        listener.generate_empty_stratagems()

        self.assertGreater(len(listener.stratagems), 0)
        self.assertIn("Mission - Reinforce", listener.stratagems)
        self.assertIn("Mission - Resupply", listener.stratagems)

    def test_generate_empty_macros(self):
        """Test generation of default macro bindings."""
        listener = KeyboardListener(self.stratagems_file, self.macros_file)
        listener.generate_empty_macros()

        self.assertEqual(len(listener.bindings), 10)
        self.assertIn("insert", listener.bindings)
        self.assertIn("home", listener.bindings)

    @patch('listener.keyboard')
    @patch('listener.time.sleep')
    def test_execute_stratagem(self, mock_sleep, mock_keyboard):
        """Test stratagem execution with mocked keyboard controller."""
        listener = KeyboardListener(self.stratagems_file, self.macros_file)
        test_sequence = ["i", "j", "k", "l"]

        listener.execute_stratagem("Test Stratagem", test_sequence)

        # Verify keyboard presses
        self.assertEqual(mock_keyboard.press.call_count, 4)
        self.assertEqual(mock_keyboard.release.call_count, 4)

    @patch('listener.keyboard')
    def test_execute_stratagem_empty_sequence(self, mock_keyboard):
        """Test that empty sequences are handled gracefully."""
        listener = KeyboardListener(self.stratagems_file, self.macros_file)

        listener.execute_stratagem("Empty Stratagem", [])

        # Should not press any keys
        mock_keyboard.press.assert_not_called()

    def test_on_press_valid_key(self):
        """Test on_press callback with a valid macro key."""
        # Write test data
        with open(self.stratagems_file, 'w') as f:
            json.dump(self.test_stratagems, f)
        with open(self.macros_file, 'w') as f:
            json.dump(self.test_macros, f)

        listener = KeyboardListener(self.stratagems_file, self.macros_file)

        # Mock the execute_stratagem method
        listener.execute_stratagem = Mock()

        # Create a mock key with name attribute
        mock_key = Mock()
        mock_key.name = "insert"

        listener.on_press(mock_key)

        # Verify execute_stratagem was called
        listener.execute_stratagem.assert_called_once()

    def test_on_press_invalid_key(self):
        """Test on_press callback with an unbound key."""
        listener = KeyboardListener(self.stratagems_file, self.macros_file)
        listener.execute_stratagem = Mock()

        # Create a mock key that's not bound
        mock_key = Mock()
        mock_key.name = "unbound_key"

        listener.on_press(mock_key)

        # Should not execute stratagem
        listener.execute_stratagem.assert_not_called()

    def test_stop(self):
        """Test stopping the listener."""
        listener = KeyboardListener(self.stratagems_file, self.macros_file)

        self.assertTrue(listener.running)
        listener.stop()
        self.assertFalse(listener.running)

    def test_thread_safety(self):
        """Test that data access is thread-safe."""
        # Write test data
        with open(self.stratagems_file, 'w') as f:
            json.dump(self.test_stratagems, f)
        with open(self.macros_file, 'w') as f:
            json.dump(self.test_macros, f)

        listener = KeyboardListener(self.stratagems_file, self.macros_file)

        # The data_lock should be used for thread-safe operations
        self.assertIsNotNone(listener.data_lock)

        # Test that we can acquire and release the lock
        listener.data_lock.acquire()
        listener.data_lock.release()


@unittest.skipIf(not LISTENER_AVAILABLE, "Listener dependencies not available")
class TestConstants(unittest.TestCase):
    """Test that timing constants are properly defined."""

    def test_timing_constants_exist(self):
        """Verify all timing constants are defined."""
        self.assertIsNotNone(STRATAGEM_ACTIVATION_DELAY)
        self.assertIsNotNone(KEY_PRESS_DURATION)
        self.assertIsNotNone(KEY_RELEASE_DELAY)

    def test_timing_constants_values(self):
        """Verify timing constants have reasonable values."""
        self.assertEqual(STRATAGEM_ACTIVATION_DELAY, 0.1)
        self.assertEqual(KEY_PRESS_DURATION, 0.05)
        self.assertEqual(KEY_RELEASE_DELAY, 0.05)


@unittest.skipIf(not LISTENER_AVAILABLE, "Listener dependencies not available")
class TestListenerErrorHandling(unittest.TestCase):
    """Test error handling in KeyboardListener."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.stratagems_file = os.path.join(self.test_dir, "test_stratagems.json")
        self.macros_file = os.path.join(self.test_dir, "test_macros.json")

    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.stratagems_file):
            os.remove(self.stratagems_file)
        if os.path.exists(self.macros_file):
            os.remove(self.macros_file)
        os.rmdir(self.test_dir)

    def test_load_stratagems_permission_error(self):
        """Test handling of permission errors when loading stratagems."""
        # Create a file with no read permissions
        with open(self.stratagems_file, 'w') as f:
            json.dump({"test": ["i"]}, f)
        os.chmod(self.stratagems_file, 0o000)

        try:
            listener = KeyboardListener(self.stratagems_file, self.macros_file)
            # Should fall back to default stratagems
            self.assertGreater(len(listener.stratagems), 0)
        finally:
            # Restore permissions for cleanup
            os.chmod(self.stratagems_file, 0o644)

    def test_load_stratagems_empty_file(self):
        """Test loading from an empty file."""
        with open(self.stratagems_file, 'w') as f:
            f.write("")

        listener = KeyboardListener(self.stratagems_file, self.macros_file)
        # Should generate defaults
        self.assertGreater(len(listener.stratagems), 0)

    def test_load_macros_corrupt_data(self):
        """Test loading macros with corrupt data."""
        with open(self.macros_file, 'w') as f:
            f.write('{"insert": }')  # Invalid JSON

        listener = KeyboardListener(self.stratagems_file, self.macros_file)
        # Should fall back to defaults
        self.assertGreater(len(listener.bindings), 0)

    def test_on_press_with_exception(self):
        """Test on_press handles exceptions gracefully."""
        listener = KeyboardListener(self.stratagems_file, self.macros_file)

        # Create a mock key that will raise an exception
        mock_key = Mock()
        mock_key.name = Mock(side_effect=Exception("Test exception"))

        # Should not crash
        listener.on_press(mock_key)

    def test_on_press_with_none_key(self):
        """Test on_press with None key."""
        listener = KeyboardListener(self.stratagems_file, self.macros_file)
        listener.execute_stratagem = Mock()

        listener.on_press(None)

        # Should not execute anything
        listener.execute_stratagem.assert_not_called()

    @patch('listener.keyboard')
    def test_execute_stratagem_with_keyboard_error(self, mock_keyboard):
        """Test execute_stratagem when keyboard press fails."""
        listener = KeyboardListener(self.stratagems_file, self.macros_file)

        # Make keyboard.press raise an exception
        mock_keyboard.press.side_effect = Exception("Keyboard error")

        # Should not crash
        listener.execute_stratagem("Test", ["i", "j"])

    def test_concurrent_data_access(self):
        """Test that concurrent data access is thread-safe."""
        import threading

        test_stratagems = {"Test": ["i", "j", "k"]}
        with open(self.stratagems_file, 'w') as f:
            json.dump(test_stratagems, f)
        with open(self.macros_file, 'w') as f:
            json.dump({"insert": "Test"}, f)

        listener = KeyboardListener(self.stratagems_file, self.macros_file)

        def read_data():
            for _ in range(100):
                with listener.data_lock:
                    _ = listener.stratagems.copy()
                    _ = listener.bindings.copy()

        threads = [threading.Thread(target=read_data) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # If we get here without deadlock or errors, test passed

    def test_load_stratagems_with_invalid_types(self):
        """Test loading stratagems with invalid data types."""
        with open(self.stratagems_file, 'w') as f:
            json.dump({"test": "not_a_list"}, f)

        listener = KeyboardListener(self.stratagems_file, self.macros_file)
        # Should load the data even if types are wrong
        # (validation happens elsewhere)
        self.assertIsInstance(listener.stratagems, dict)


@unittest.skipIf(not LISTENER_AVAILABLE, "Listener dependencies not available")
class TestListenerEdgeCases(unittest.TestCase):
    """Test edge cases for KeyboardListener."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.stratagems_file = os.path.join(self.test_dir, "test_stratagems.json")
        self.macros_file = os.path.join(self.test_dir, "test_macros.json")

    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.stratagems_file):
            os.remove(self.stratagems_file)
        if os.path.exists(self.macros_file):
            os.remove(self.macros_file)
        os.rmdir(self.test_dir)

    @patch('listener.keyboard')
    @patch('listener.time.sleep')
    def test_execute_very_long_sequence(self, mock_sleep, mock_keyboard):
        """Test executing a very long stratagem sequence."""
        listener = KeyboardListener(self.stratagems_file, self.macros_file)
        long_sequence = ["i", "j", "k", "l"] * 100  # 400 key presses

        listener.execute_stratagem("Long Stratagem", long_sequence)

        # Should press all keys
        self.assertEqual(mock_keyboard.press.call_count, 400)
        self.assertEqual(mock_keyboard.release.call_count, 400)

    @patch('listener.keyboard')
    def test_execute_single_key_sequence(self, mock_keyboard):
        """Test executing a single-key stratagem."""
        listener = KeyboardListener(self.stratagems_file, self.macros_file)

        listener.execute_stratagem("Single", ["i"])

        mock_keyboard.press.assert_called_once()
        mock_keyboard.release.assert_called_once()

    def test_on_press_with_char_key(self):
        """Test on_press with a character key (has .char attribute)."""
        test_data = {"Test": ["i"]}
        with open(self.stratagems_file, 'w') as f:
            json.dump(test_data, f)
        with open(self.macros_file, 'w') as f:
            json.dump({"a": "Test"}, f)

        listener = KeyboardListener(self.stratagems_file, self.macros_file)
        listener.execute_stratagem = Mock()

        # Mock a character key
        mock_key = Mock()
        mock_key.char = "a"
        delattr(mock_key, 'name')  # Character keys don't have name

        listener.on_press(mock_key)

        listener.execute_stratagem.assert_called_once()

    def test_stop_when_not_running(self):
        """Test stopping an already stopped listener."""
        listener = KeyboardListener(self.stratagems_file, self.macros_file)

        listener.stop()
        self.assertFalse(listener.running)

        # Stopping again should be safe
        listener.stop()
        self.assertFalse(listener.running)

    def test_multiple_listeners(self):
        """Test creating multiple listener instances."""
        listener1 = KeyboardListener(self.stratagems_file, self.macros_file)
        listener2 = KeyboardListener(self.stratagems_file, self.macros_file)

        # Both should be independent
        self.assertIsNot(listener1.stratagems, listener2.stratagems)
        self.assertIsNot(listener1.bindings, listener2.bindings)
        self.assertIsNot(listener1.data_lock, listener2.data_lock)

    def test_generate_defaults_produces_valid_data(self):
        """Test that generated defaults are valid."""
        listener = KeyboardListener(self.stratagems_file, self.macros_file)

        # All stratagems should have sequences
        for name, sequence in listener.stratagems.items():
            self.assertIsInstance(sequence, list)
            self.assertGreater(len(sequence), 0)
            for key in sequence:
                self.assertIn(key, ['i', 'j', 'k', 'l'])

        # All bindings should have assignments
        for key, stratagem in listener.bindings.items():
            self.assertIsInstance(key, str)
            self.assertIsInstance(stratagem, str)


if __name__ == '__main__':
    unittest.main()
