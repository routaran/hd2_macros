"""
Comprehensive unit tests for the Tkinter GUI module.
"""

import unittest
import os
import tempfile
import json
from unittest.mock import Mock, patch, MagicMock, call

# Try to import tkinter and gui - skip tests if unavailable
try:
    import tkinter as tk
    from gui import MacroGUI, VALID_STRATAGEM_KEYS, BACKUP_DIR, ComboDialog, CustomDialog
    TKINTER_AVAILABLE = True
except (ImportError, Exception):
    TKINTER_AVAILABLE = False


@unittest.skipIf(not TKINTER_AVAILABLE, "Tkinter not available")
class TestMacroGUIComprehensive(unittest.TestCase):
    """Comprehensive test cases for MacroGUI class."""

    def setUp(self):
        """Set up test fixtures."""
        self.root = tk.Tk()
        self.root.withdraw()  # Hide window during tests

        # Create mock listener
        self.mock_listener = Mock()
        self.mock_listener.stratagems = {
            "Test Stratagem": ["i", "j", "k", "l"],
            "Mission - Reinforce": ["i", "k", "l", "j", "i"],
            "Mission - Resupply": ["k", "k", "i", "l"]
        }
        self.mock_listener.bindings = {
            "insert": "Test Stratagem",
            "home": "Mission - Reinforce",
            "page_up": "Unassigned"
        }

        # Create temporary files
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
                try:
                    os.remove(os.path.join(self.test_dir, file))
                except:
                    pass
            try:
                os.rmdir(self.test_dir)
            except:
                pass

    def test_initialization_with_no_data(self):
        """Test GUI initialization with empty stratagems and bindings."""
        self.mock_listener.stratagems = {}
        self.mock_listener.bindings = {}

        with patch.object(MacroGUI, 'start_listener'):
            gui = MacroGUI(self.root, self.mock_listener)

            self.assertEqual(len(gui.stratagems), 0)
            self.assertEqual(len(gui.bindings), 0)

    def test_validation_empty_string(self):
        """Test validation rejects empty strings."""
        with patch.object(MacroGUI, 'start_listener'):
            gui = MacroGUI(self.root, self.mock_listener)

            is_valid, msg = gui.validate_stratagem_keys("")
            self.assertFalse(is_valid)
            self.assertIn("empty", msg.lower())

    def test_validation_whitespace_only(self):
        """Test validation rejects whitespace-only strings."""
        with patch.object(MacroGUI, 'start_listener'):
            gui = MacroGUI(self.root, self.mock_listener)

            is_valid, msg = gui.validate_stratagem_keys("   ")
            self.assertFalse(is_valid)

    def test_validation_single_invalid_char(self):
        """Test validation catches single invalid character."""
        with patch.object(MacroGUI, 'start_listener'):
            gui = MacroGUI(self.root, self.mock_listener)

            is_valid, msg = gui.validate_stratagem_keys("x")
            self.assertFalse(is_valid)
            self.assertIn("x", msg)

    def test_validation_mixed_valid_invalid(self):
        """Test validation with mix of valid and invalid chars."""
        with patch.object(MacroGUI, 'start_listener'):
            gui = MacroGUI(self.root, self.mock_listener)

            is_valid, msg = gui.validate_stratagem_keys("ijklxyz")
            self.assertFalse(is_valid)
            self.assertIn("x", msg)
            self.assertIn("y", msg)
            self.assertIn("z", msg)

    def test_validation_all_valid_keys(self):
        """Test validation passes with all valid keys."""
        with patch.object(MacroGUI, 'start_listener'):
            gui = MacroGUI(self.root, self.mock_listener)

            is_valid, msg = gui.validate_stratagem_keys("ijklijkl")
            self.assertTrue(is_valid)
            self.assertEqual(msg, "")

    def test_validation_case_sensitivity(self):
        """Test that validation is case-sensitive."""
        with patch.object(MacroGUI, 'start_listener'):
            gui = MacroGUI(self.root, self.mock_listener)

            # Uppercase should be invalid
            is_valid, msg = gui.validate_stratagem_keys("IJKL")
            self.assertFalse(is_valid)

    @patch('gui.shutil.copy2')
    @patch('gui.os.path.exists', return_value=True)
    def test_backup_file_success(self, mock_exists, mock_copy):
        """Test successful file backup."""
        with patch.object(MacroGUI, 'start_listener'):
            gui = MacroGUI(self.root, self.mock_listener)

            test_file = "/test/file.json"
            gui.backup_file(test_file)

            mock_copy.assert_called_once()
            # Verify backup path includes timestamp
            backup_path = mock_copy.call_args[0][1]
            self.assertIn("backups", backup_path)
            self.assertIn(".backup", backup_path)

    @patch('gui.shutil.copy2', side_effect=PermissionError("Access denied"))
    @patch('gui.os.path.exists', return_value=True)
    def test_backup_file_permission_error(self, mock_exists, mock_copy):
        """Test backup handles permission errors gracefully."""
        with patch.object(MacroGUI, 'start_listener'):
            gui = MacroGUI(self.root, self.mock_listener)

            # Should not crash
            gui.backup_file("/test/file.json")

    @patch('gui.os.path.exists', return_value=False)
    def test_backup_file_nonexistent(self, mock_exists):
        """Test backup skips non-existent files."""
        with patch.object(MacroGUI, 'start_listener'):
            gui = MacroGUI(self.root, self.mock_listener)

            # Should not attempt to copy
            with patch('gui.shutil.copy2') as mock_copy:
                gui.backup_file("/nonexistent/file.json")
                mock_copy.assert_not_called()

    def test_update_status(self):
        """Test status bar update."""
        with patch.object(MacroGUI, 'start_listener'):
            gui = MacroGUI(self.root, self.mock_listener)

            messages = ["Test 1", "Test 2", ""]
            for msg in messages:
                gui.update_status(msg)
                self.assertEqual(gui.status_var.get(), msg)

    @patch('gui.messagebox.showinfo')
    def test_save_all_calls_both_saves(self, mock_messagebox):
        """Test save_all calls both save methods."""
        with patch.object(MacroGUI, 'start_listener'):
            gui = MacroGUI(self.root, self.mock_listener)

            with patch.object(gui, 'save_stratagems') as mock_save_strat, \
                 patch.object(gui, 'save_bindings') as mock_save_bind:
                gui.save_all()

                mock_save_strat.assert_called_once()
                mock_save_bind.assert_called_once()
                mock_messagebox.assert_called_once()

    @patch('builtins.open', create=True)
    @patch('gui.json.dump')
    def test_save_stratagems_creates_backup(self, mock_json, mock_open):
        """Test that saving stratagems creates a backup."""
        with patch.object(MacroGUI, 'start_listener'):
            gui = MacroGUI(self.root, self.mock_listener)

            with patch.object(gui, 'backup_file') as mock_backup:
                gui.save_stratagems()
                mock_backup.assert_called_once()

    @patch('gui.messagebox.showerror')
    @patch('builtins.open', side_effect=OSError("Disk full"))
    def test_save_stratagems_handles_os_error(self, mock_open, mock_error):
        """Test save_stratagems handles OS errors."""
        with patch.object(MacroGUI, 'start_listener'):
            gui = MacroGUI(self.root, self.mock_listener)

            with patch.object(gui, 'backup_file'):
                gui.save_stratagems()
                mock_error.assert_called_once()

    @patch('gui.messagebox.showinfo')
    @patch('gui.messagebox.showerror')
    @patch('gui.CustomDialog')
    def test_add_stratagem_with_empty_name(self, mock_dialog, mock_error, mock_info):
        """Test adding stratagem with empty name."""
        with patch.object(MacroGUI, 'start_listener'):
            gui = MacroGUI(self.root, self.mock_listener)

            mock_dialog.return_value.result = ""
            gui.add_stratagem()

            # Should not call save or show success
            mock_info.assert_not_called()

    @patch('gui.messagebox.showinfo')
    @patch('gui.messagebox.showwarning')
    @patch('gui.CustomDialog')
    def test_add_stratagem_duplicate_name(self, mock_dialog, mock_warning, mock_info):
        """Test adding stratagem with duplicate name."""
        with patch.object(MacroGUI, 'start_listener'):
            gui = MacroGUI(self.root, self.mock_listener)

            # Try to add duplicate (case-insensitive)
            mock_dialog_instance = Mock()
            mock_dialog_instance.result = "test stratagem"
            mock_dialog.return_value = mock_dialog_instance

            gui.add_stratagem()

            mock_warning.assert_called_once()
            mock_info.assert_not_called()

    @patch('gui.messagebox.showinfo')
    @patch('gui.messagebox.showerror')
    @patch('gui.CustomDialog')
    def test_add_stratagem_invalid_keys(self, mock_dialog, mock_error, mock_info):
        """Test adding stratagem with invalid keys."""
        with patch.object(MacroGUI, 'start_listener'):
            gui = MacroGUI(self.root, self.mock_listener)

            call_count = [0]

            def mock_result(*args, **kwargs):
                call_count[0] += 1
                if call_count[0] == 1:
                    return "New Stratagem"
                else:
                    return "xyz"  # Invalid keys

            mock_dialog_instance = Mock()
            mock_dialog_instance.result = property(lambda self: mock_result())
            mock_dialog.return_value = mock_dialog_instance

            with patch.object(gui, 'save_stratagems'):
                gui.add_stratagem()

                mock_error.assert_called()
                mock_info.assert_not_called()

    @patch('gui.messagebox.showinfo')
    @patch('gui.CustomDialog')
    def test_add_stratagem_success(self, mock_dialog, mock_info):
        """Test successful stratagem addition."""
        with patch.object(MacroGUI, 'start_listener'):
            gui = MacroGUI(self.root, self.mock_listener)

            call_count = [0]

            def side_effect(*args):
                call_count[0] += 1
                instance = Mock()
                if call_count[0] == 1:
                    instance.result = "New Stratagem"
                else:
                    instance.result = "ijkl"
                return instance

            mock_dialog.side_effect = side_effect

            with patch.object(gui, 'save_stratagems'):
                initial_count = len(gui.stratagems)
                gui.add_stratagem()

                self.assertEqual(len(gui.stratagems), initial_count + 1)
                self.assertIn("New Stratagem", gui.stratagems)
                mock_info.assert_called_once()

    @patch('gui.messagebox.showwarning')
    @patch('gui.ComboDialog')
    def test_edit_stratagem_no_stratagems(self, mock_dialog, mock_warning):
        """Test editing when no stratagems exist."""
        with patch.object(MacroGUI, 'start_listener'):
            gui = MacroGUI(self.root, self.mock_listener)
            gui.stratagems = {}

            gui.edit_stratagem()

            mock_warning.assert_called_once()
            mock_dialog.assert_not_called()

    @patch('gui.messagebox.showinfo')
    @patch('gui.CustomDialog')
    @patch('gui.ComboDialog')
    def test_edit_stratagem_cancel_selection(self, mock_combo, mock_custom, mock_info):
        """Test editing stratagem when user cancels selection."""
        with patch.object(MacroGUI, 'start_listener'):
            gui = MacroGUI(self.root, self.mock_listener)

            mock_combo.return_value.result = None
            gui.edit_stratagem()

            mock_custom.assert_not_called()
            mock_info.assert_not_called()

    @patch('gui.messagebox.showinfo')
    @patch('gui.messagebox.showerror')
    @patch('gui.CustomDialog')
    @patch('gui.ComboDialog')
    def test_edit_stratagem_invalid_new_keys(self, mock_combo, mock_custom, mock_error, mock_info):
        """Test editing stratagem with invalid new keys."""
        with patch.object(MacroGUI, 'start_listener'):
            gui = MacroGUI(self.root, self.mock_listener)

            mock_combo.return_value.result = "Test Stratagem"
            mock_custom.return_value.result = "abc"  # Invalid

            gui.edit_stratagem()

            mock_error.assert_called_once()
            mock_info.assert_not_called()

    @patch('gui.messagebox.showwarning')
    @patch('gui.ComboDialog')
    def test_delete_stratagem_no_stratagems(self, mock_dialog, mock_warning):
        """Test deleting when no stratagems exist."""
        with patch.object(MacroGUI, 'start_listener'):
            gui = MacroGUI(self.root, self.mock_listener)
            gui.stratagems = {}

            gui.delete_stratagem()

            mock_warning.assert_called_once()

    @patch('gui.messagebox.showinfo')
    @patch('gui.messagebox.askyesno', return_value=False)
    @patch('gui.ComboDialog')
    def test_delete_stratagem_user_cancels(self, mock_dialog, mock_confirm, mock_info):
        """Test deleting stratagem when user cancels confirmation."""
        with patch.object(MacroGUI, 'start_listener'):
            gui = MacroGUI(self.root, self.mock_listener)

            mock_dialog.return_value.result = "Test Stratagem"
            initial_count = len(gui.stratagems)

            gui.delete_stratagem()

            # Should not delete
            self.assertEqual(len(gui.stratagems), initial_count)
            mock_info.assert_not_called()

    @patch('gui.messagebox.showinfo')
    @patch('gui.messagebox.askyesno', return_value=True)
    @patch('gui.ComboDialog')
    def test_delete_stratagem_updates_bindings(self, mock_dialog, mock_confirm, mock_info):
        """Test that deleting stratagem updates bindings."""
        with patch.object(MacroGUI, 'start_listener'):
            gui = MacroGUI(self.root, self.mock_listener)

            mock_dialog.return_value.result = "Test Stratagem"

            with patch.object(gui, 'save_stratagems'), \
                 patch.object(gui, 'save_bindings'):
                gui.delete_stratagem()

                # Bound key should now be "Unassigned"
                self.assertEqual(gui.bindings["insert"], "Unassigned")

    def test_on_close_stops_listener(self):
        """Test that closing window stops the listener."""
        with patch.object(MacroGUI, 'start_listener'):
            gui = MacroGUI(self.root, self.mock_listener)
            gui.listener.running = True

            gui.on_close()

            gui.listener.stop.assert_called_once()

    def test_on_close_without_running_listener(self):
        """Test closing when listener is not running."""
        with patch.object(MacroGUI, 'start_listener'):
            gui = MacroGUI(self.root, self.mock_listener)
            gui.listener.running = False

            # Should not crash
            gui.on_close()


@unittest.skipIf(not TKINTER_AVAILABLE, "Tkinter not available")
class TestDialogs(unittest.TestCase):
    """Test custom dialog classes."""

    def setUp(self):
        """Set up test fixtures."""
        self.root = tk.Tk()
        self.root.withdraw()

    def tearDown(self):
        """Clean up test fixtures."""
        try:
            self.root.destroy()
        except:
            pass

    def test_combo_dialog_with_empty_list(self):
        """Test ComboDialog with empty stratagem list."""
        dialog = ComboDialog(self.root, stratagems=[])
        # Should initialize without error
        self.assertEqual(dialog.stratagems, [])

    def test_combo_dialog_with_none_list(self):
        """Test ComboDialog with None stratagem list."""
        dialog = ComboDialog(self.root, stratagems=None)
        # Should default to empty list
        self.assertEqual(dialog.stratagems, [])


@unittest.skipIf(not TKINTER_AVAILABLE, "Tkinter not available")
class TestIntegration(unittest.TestCase):
    """Integration tests for complete workflows."""

    def setUp(self):
        """Set up test fixtures."""
        self.root = tk.Tk()
        self.root.withdraw()

        self.mock_listener = Mock()
        self.mock_listener.stratagems = {
            "Test": ["i", "j"]
        }
        self.mock_listener.bindings = {
            "insert": "Test"
        }

        self.test_dir = tempfile.mkdtemp()
        self.mock_listener.stratagems_file = os.path.join(self.test_dir, "stratagems.json")
        self.mock_listener.macro_file = os.path.join(self.test_dir, "macros.json")
        self.mock_listener.running = False

    def tearDown(self):
        """Clean up."""
        try:
            self.root.destroy()
        except:
            pass

        if os.path.exists(self.test_dir):
            for file in os.listdir(self.test_dir):
                try:
                    os.remove(os.path.join(self.test_dir, file))
                except:
                    pass
            try:
                os.rmdir(self.test_dir)
            except:
                pass

    @patch('gui.messagebox.showinfo')
    @patch('gui.messagebox.askyesno', return_value=True)
    @patch('gui.ComboDialog')
    @patch('gui.CustomDialog')
    def test_full_workflow_add_edit_delete(self, mock_custom, mock_combo, mock_confirm, mock_info):
        """Test complete workflow: add, edit, then delete a stratagem."""
        with patch.object(MacroGUI, 'start_listener'):
            gui = MacroGUI(self.root, self.mock_listener)

            # Add stratagem
            call_count = [0]

            def custom_side_effect(*args):
                call_count[0] += 1
                instance = Mock()
                if call_count[0] == 1:  # Name
                    instance.result = "Workflow Test"
                elif call_count[0] == 2:  # Keys for add
                    instance.result = "ijkl"
                else:  # Keys for edit
                    instance.result = "lkji"
                return instance

            mock_custom.side_effect = custom_side_effect

            with patch.object(gui, 'save_stratagems'), \
                 patch.object(gui, 'save_bindings'):
                # Add
                gui.add_stratagem()
                self.assertIn("Workflow Test", gui.stratagems)

                # Edit
                mock_combo.return_value.result = "Workflow Test"
                gui.edit_stratagem()
                self.assertEqual(gui.stratagems["Workflow Test"], ['l', 'k', 'j', 'i'])

                # Delete
                gui.delete_stratagem()
                self.assertNotIn("Workflow Test", gui.stratagems)


if __name__ == '__main__':
    unittest.main()
