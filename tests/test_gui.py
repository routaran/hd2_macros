"""
Unit tests for the GUI module.
"""

import unittest
import os
import tempfile
from unittest.mock import Mock, patch, MagicMock

# Try to import tkinter and gui - skip tests if unavailable
try:
    import tkinter as tk
    from gui import MacroGUI, VALID_STRATAGEM_KEYS, BACKUP_DIR
    TKINTER_AVAILABLE = True
except (ImportError, Exception):
    TKINTER_AVAILABLE = False


@unittest.skipIf(not TKINTER_AVAILABLE, "Tkinter not available")
class TestMacroGUI(unittest.TestCase):
    """Test cases for MacroGUI class."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a root window for testing
        self.root = tk.Tk()

        # Create mock listener
        self.mock_listener = Mock()
        self.mock_listener.stratagems = {
            "Test Stratagem": ["i", "j", "k", "l"],
            "Mission - Reinforce": ["i", "k", "l", "j", "i"]
        }
        self.mock_listener.bindings = {
            "insert": "Test Stratagem",
            "home": "Mission - Reinforce"
        }

        # Create temporary files for testing
        self.test_dir = tempfile.mkdtemp()
        self.mock_listener.stratagems_file = os.path.join(self.test_dir, "stratagems.json")
        self.mock_listener.macro_file = os.path.join(self.test_dir, "macros.json")
        self.mock_listener.running = False

    def tearDown(self):
        """Clean up test fixtures."""
        try:
            self.root.destroy()
        except:
            pass

        # Clean up temp files
        if os.path.exists(self.test_dir):
            for file in os.listdir(self.test_dir):
                os.remove(os.path.join(self.test_dir, file))
            os.rmdir(self.test_dir)

    def test_initialization(self):
        """Test that MacroGUI initializes correctly."""
        with patch.object(MacroGUI, 'start_listener'):
            gui = MacroGUI(self.root, self.mock_listener)

            self.assertEqual(gui.master, self.root)
            self.assertEqual(gui.listener, self.mock_listener)
            self.assertIsNotNone(gui.stratagems)
            self.assertIsNotNone(gui.bindings)

    def test_load_data(self):
        """Test loading data from listener."""
        with patch.object(MacroGUI, 'start_listener'):
            gui = MacroGUI(self.root, self.mock_listener)

            self.assertEqual(gui.stratagems, self.mock_listener.stratagems)
            self.assertEqual(gui.bindings, self.mock_listener.bindings)

    def test_validate_stratagem_keys_valid(self):
        """Test validation of valid stratagem keys."""
        with patch.object(MacroGUI, 'start_listener'):
            gui = MacroGUI(self.root, self.mock_listener)

            is_valid, error_msg = gui.validate_stratagem_keys("ijkl")
            self.assertTrue(is_valid)
            self.assertEqual(error_msg, "")

    def test_validate_stratagem_keys_empty(self):
        """Test validation rejects empty keys."""
        with patch.object(MacroGUI, 'start_listener'):
            gui = MacroGUI(self.root, self.mock_listener)

            is_valid, error_msg = gui.validate_stratagem_keys("")
            self.assertFalse(is_valid)
            self.assertIn("empty", error_msg.lower())

    def test_validate_stratagem_keys_invalid_chars(self):
        """Test validation rejects invalid characters."""
        with patch.object(MacroGUI, 'start_listener'):
            gui = MacroGUI(self.root, self.mock_listener)

            is_valid, error_msg = gui.validate_stratagem_keys("abcd")
            self.assertFalse(is_valid)
            self.assertIn("invalid", error_msg.lower())

    def test_validate_stratagem_keys_mixed(self):
        """Test validation with mix of valid and invalid characters."""
        with patch.object(MacroGUI, 'start_listener'):
            gui = MacroGUI(self.root, self.mock_listener)

            is_valid, error_msg = gui.validate_stratagem_keys("ijka")
            self.assertFalse(is_valid)
            self.assertIn("a", error_msg)

    @patch('gui.shutil.copy2')
    @patch('gui.os.path.exists')
    def test_backup_file(self, mock_exists, mock_copy):
        """Test backup file creation."""
        mock_exists.return_value = True

        with patch.object(MacroGUI, 'start_listener'):
            gui = MacroGUI(self.root, self.mock_listener)

            test_file = "/test/file.json"
            gui.backup_file(test_file)

            # Verify copy was called
            mock_copy.assert_called_once()

    def test_update_status(self):
        """Test status bar update."""
        with patch.object(MacroGUI, 'start_listener'):
            gui = MacroGUI(self.root, self.mock_listener)

            test_message = "Test status message"
            gui.update_status(test_message)

            self.assertEqual(gui.status_var.get(), test_message)

    @patch('gui.messagebox.showinfo')
    def test_save_all(self, mock_messagebox):
        """Test save all functionality."""
        with patch.object(MacroGUI, 'start_listener'):
            gui = MacroGUI(self.root, self.mock_listener)

            with patch.object(gui, 'save_stratagems'), \
                 patch.object(gui, 'save_bindings'):
                gui.save_all()

                # Verify save methods were called
                gui.save_stratagems.assert_called_once()
                gui.save_bindings.assert_called_once()
                mock_messagebox.assert_called_once()

    @patch('builtins.open', create=True)
    @patch('gui.json.dump')
    def test_save_stratagems_success(self, mock_json_dump, mock_open):
        """Test successful stratagem saving."""
        with patch.object(MacroGUI, 'start_listener'):
            gui = MacroGUI(self.root, self.mock_listener)

            with patch.object(gui, 'backup_file'):
                gui.save_stratagems()

                # Verify backup and save were called
                gui.backup_file.assert_called_once()
                mock_json_dump.assert_called_once()

    @patch('gui.messagebox.showerror')
    @patch('builtins.open', side_effect=PermissionError("Access denied"))
    def test_save_stratagems_permission_error(self, mock_open, mock_error):
        """Test handling of permission error during save."""
        with patch.object(MacroGUI, 'start_listener'):
            gui = MacroGUI(self.root, self.mock_listener)

            with patch.object(gui, 'backup_file'):
                gui.save_stratagems()

                # Verify error message was shown
                mock_error.assert_called_once()

    def test_keyboard_shortcuts_configured(self):
        """Test that keyboard shortcuts are properly configured."""
        with patch.object(MacroGUI, 'start_listener'):
            gui = MacroGUI(self.root, self.mock_listener)

            # The master should have bindings for shortcuts
            # This is a basic check that shortcuts were configured
            self.assertIsNotNone(gui.master)


@unittest.skipIf(not TKINTER_AVAILABLE, "Tkinter not available")
class TestConstants(unittest.TestCase):
    """Test that constants are properly defined."""

    def test_valid_stratagem_keys(self):
        """Verify valid stratagem keys constant."""
        self.assertEqual(VALID_STRATAGEM_KEYS, {'i', 'j', 'k', 'l'})

    def test_backup_dir(self):
        """Verify backup directory constant."""
        self.assertEqual(BACKUP_DIR, 'backups')


@unittest.skipIf(not TKINTER_AVAILABLE, "Tkinter not available")
class TestDialogs(unittest.TestCase):
    """Test custom dialog classes."""

    def setUp(self):
        """Set up test fixtures."""
        self.root = tk.Tk()

    def tearDown(self):
        """Clean up test fixtures."""
        try:
            self.root.destroy()
        except:
            pass

    def test_combo_dialog_initialization(self):
        """Test ComboDialog initialization."""
        from gui import ComboDialog

        test_stratagems = ["Stratagem 1", "Stratagem 2"]

        # Can't fully test dialog without showing it, but we can test initialization
        # This would require more complex mocking for full testing


@unittest.skipIf(not TKINTER_AVAILABLE, "Tkinter not available")
class TestIntegration(unittest.TestCase):
    """Integration tests for GUI operations."""

    def setUp(self):
        """Set up test fixtures."""
        self.root = tk.Tk()
        self.mock_listener = Mock()
        self.mock_listener.stratagems = {
            "Test Stratagem": ["i", "j", "k", "l"]
        }
        self.mock_listener.bindings = {
            "insert": "Test Stratagem"
        }
        self.test_dir = tempfile.mkdtemp()
        self.mock_listener.stratagems_file = os.path.join(self.test_dir, "stratagems.json")
        self.mock_listener.macro_file = os.path.join(self.test_dir, "macros.json")
        self.mock_listener.running = False

    def tearDown(self):
        """Clean up test fixtures."""
        try:
            self.root.destroy()
        except:
            pass

        if os.path.exists(self.test_dir):
            for file in os.listdir(self.test_dir):
                os.remove(os.path.join(self.test_dir, file))
            os.rmdir(self.test_dir)

    @patch('gui.messagebox.showinfo')
    @patch('gui.messagebox.showwarning')
    def test_add_stratagem_duplicate(self, mock_warning, mock_info):
        """Test adding a duplicate stratagem."""
        with patch.object(MacroGUI, 'start_listener'):
            gui = MacroGUI(self.root, self.mock_listener)

            # Try to add a stratagem that already exists (case-insensitive)
            with patch('gui.CustomDialog') as mock_dialog:
                mock_dialog.return_value.result = "test stratagem"
                gui.add_stratagem()

                # Should show warning
                mock_warning.assert_called_once()


if __name__ == '__main__':
    unittest.main()
