"""
Unit tests for the KeyboardListener module.
"""

import unittest
import json
import os
import tempfile
from unittest.mock import Mock, patch, MagicMock
from listener import KeyboardListener, STRATAGEM_ACTIVATION_DELAY, KEY_PRESS_DURATION, KEY_RELEASE_DELAY


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


if __name__ == '__main__':
    unittest.main()
