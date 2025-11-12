"""
Comprehensive unit tests for the PyQt6 GUI module.
"""

import unittest
import sys
import os
import tempfile
import json
from unittest.mock import Mock, patch, MagicMock

# Import PyQt6 (tests will be skipped if not available)
try:
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtTest import QTest
    from PyQt6.QtCore import Qt
    from gui_qt import (
        MacroGUI, MacroKeyWidget, StratagemDialog,
        AddStratagemDialog, VALID_STRATAGEM_KEYS, COLORS
    )
    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False


@unittest.skipIf(not PYQT_AVAILABLE, "PyQt6 not available")
class TestMacroGUIPyQt(unittest.TestCase):
    """Test cases for PyQt6 MacroGUI class."""

    @classmethod
    def setUpClass(cls):
        """Create QApplication instance for all tests."""
        if PYQT_AVAILABLE and not QApplication.instance():
            cls.app = QApplication(sys.argv)
        else:
            cls.app = QApplication.instance()

    def setUp(self):
        """Set up test fixtures."""
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

        # Create temporary files
        self.test_dir = tempfile.mkdtemp()
        self.mock_listener.stratagems_file = os.path.join(self.test_dir, "stratagems.json")
        self.mock_listener.macro_file = os.path.join(self.test_dir, "macros.json")
        self.mock_listener.running = False

    def tearDown(self):
        """Clean up test fixtures."""
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

    def test_initialization(self):
        """Test PyQt6 GUI initialization."""
        with patch.object(MacroGUI, 'start_listener'):
            gui = MacroGUI(self.mock_listener)

            self.assertIsNotNone(gui)
            self.assertEqual(gui.stratagems, self.mock_listener.stratagems)
            self.assertEqual(gui.bindings, self.mock_listener.bindings)

            gui.close()

    def test_validation_valid_keys(self):
        """Test validation with valid stratagem keys."""
        with patch.object(MacroGUI, 'start_listener'):
            gui = MacroGUI(self.mock_listener)

            is_valid, msg = gui.validate_stratagem_keys("ijkl")
            self.assertTrue(is_valid)
            self.assertEqual(msg, "")

            gui.close()

    def test_validation_invalid_keys(self):
        """Test validation with invalid keys."""
        with patch.object(MacroGUI, 'start_listener'):
            gui = MacroGUI(self.mock_listener)

            is_valid, msg = gui.validate_stratagem_keys("abc")
            self.assertFalse(is_valid)
            self.assertIn("invalid", msg.lower())

            gui.close()

    def test_validation_empty_keys(self):
        """Test validation with empty string."""
        with patch.object(MacroGUI, 'start_listener'):
            gui = MacroGUI(self.mock_listener)

            is_valid, msg = gui.validate_stratagem_keys("")
            self.assertFalse(is_valid)
            self.assertIn("empty", msg.lower())

            gui.close()

    def test_validation_whitespace_keys(self):
        """Test validation with whitespace."""
        with patch.object(MacroGUI, 'start_listener'):
            gui = MacroGUI(self.mock_listener)

            is_valid, msg = gui.validate_stratagem_keys("   ")
            self.assertFalse(is_valid)

            gui.close()

    @patch('gui_qt.shutil.copy2')
    @patch('gui_qt.os.path.exists', return_value=True)
    def test_backup_file(self, mock_exists, mock_copy):
        """Test file backup functionality."""
        with patch.object(MacroGUI, 'start_listener'):
            gui = MacroGUI(self.mock_listener)

            gui.backup_file("/test/file.json")
            mock_copy.assert_called_once()

            gui.close()

    @patch('gui_qt.QMessageBox')
    @patch('builtins.open', side_effect=PermissionError("Access denied"))
    def test_save_stratagems_permission_error(self, mock_open, mock_msgbox):
        """Test save handles permission errors."""
        with patch.object(MacroGUI, 'start_listener'):
            gui = MacroGUI(self.mock_listener)

            with patch.object(gui, 'backup_file'):
                gui.save_stratagems()
                # Should show error message
                mock_msgbox.critical.assert_called()

            gui.close()

    @patch('gui_qt.QMessageBox')
    @patch('builtins.open', side_effect=OSError("Disk full"))
    def test_save_bindings_os_error(self, mock_open, mock_msgbox):
        """Test save handles OS errors."""
        with patch.object(MacroGUI, 'start_listener'):
            gui = MacroGUI(self.mock_listener)

            with patch.object(gui, 'backup_file'):
                gui.save_bindings()
                mock_msgbox.critical.assert_called()

            gui.close()

    @patch('gui_qt.QMessageBox')
    def test_add_stratagem_empty_name(self, mock_msgbox):
        """Test adding stratagem with empty name."""
        with patch.object(MacroGUI, 'start_listener'):
            gui = MacroGUI(self.mock_listener)

            with patch('gui_qt.AddStratagemDialog') as mock_dialog:
                mock_dialog.return_value.get_data.return_value = None
                initial_count = len(gui.stratagems)

                gui.add_stratagem()

                # Should not add anything
                self.assertEqual(len(gui.stratagems), initial_count)

            gui.close()

    @patch('gui_qt.QMessageBox')
    def test_add_stratagem_duplicate(self, mock_msgbox):
        """Test adding duplicate stratagem."""
        with patch.object(MacroGUI, 'start_listener'):
            gui = MacroGUI(self.mock_listener)

            with patch('gui_qt.AddStratagemDialog') as mock_dialog:
                mock_dialog.return_value.get_data.return_value = ("test stratagem", "ijkl")

                gui.add_stratagem()

                # Should show warning
                mock_msgbox.warning.assert_called()

            gui.close()

    @patch('gui_qt.QMessageBox')
    def test_add_stratagem_invalid_keys(self, mock_msgbox):
        """Test adding stratagem with invalid keys."""
        with patch.object(MacroGUI, 'start_listener'):
            gui = MacroGUI(self.mock_listener)

            with patch('gui_qt.AddStratagemDialog') as mock_dialog:
                mock_dialog.return_value.get_data.return_value = ("New Strat", "xyz")

                gui.add_stratagem()

                # Should show error
                mock_msgbox.critical.assert_called()

            gui.close()

    @patch('gui_qt.QMessageBox')
    def test_add_stratagem_success(self, mock_msgbox):
        """Test successful stratagem addition."""
        with patch.object(MacroGUI, 'start_listener'):
            gui = MacroGUI(self.mock_listener)

            with patch('gui_qt.AddStratagemDialog') as mock_dialog, \
                 patch.object(gui, 'save_stratagems'), \
                 patch.object(gui, 'populate_stratagem_list'):
                mock_dialog.return_value.get_data.return_value = ("New Strat", "ijkl")

                initial_count = len(gui.stratagems)
                gui.add_stratagem()

                self.assertEqual(len(gui.stratagems), initial_count + 1)
                self.assertIn("New Strat", gui.stratagems)
                mock_msgbox.information.assert_called()

            gui.close()

    @patch('gui_qt.QMessageBox')
    def test_edit_stratagem_no_stratagems(self, mock_msgbox):
        """Test editing when no stratagems exist."""
        with patch.object(MacroGUI, 'start_listener'):
            gui = MacroGUI(self.mock_listener)
            gui.stratagems = {}

            gui.edit_stratagem()

            mock_msgbox.warning.assert_called()

            gui.close()

    @patch('gui_qt.QMessageBox')
    def test_delete_stratagem_no_confirmation(self, mock_msgbox):
        """Test deleting stratagem when user cancels."""
        with patch.object(MacroGUI, 'start_listener'):
            gui = MacroGUI(self.mock_listener)

            with patch('gui_qt.StratagemDialog') as mock_dialog:
                mock_dialog.return_value.get_selected.return_value = "Test Stratagem"
                mock_msgbox.question.return_value = mock_msgbox.StandardButton.No

                initial_count = len(gui.stratagems)
                gui.delete_stratagem()

                # Should not delete
                self.assertEqual(len(gui.stratagems), initial_count)

            gui.close()

    @patch('gui_qt.QMessageBox')
    def test_delete_stratagem_updates_bindings(self, mock_msgbox):
        """Test that deleting updates bindings."""
        with patch.object(MacroGUI, 'start_listener'):
            gui = MacroGUI(self.mock_listener)

            with patch('gui_qt.StratagemDialog') as mock_dialog, \
                 patch.object(gui, 'save_stratagems'), \
                 patch.object(gui, 'save_bindings'), \
                 patch.object(gui, 'populate_stratagem_list'):
                mock_dialog.return_value.get_selected.return_value = "Test Stratagem"
                mock_msgbox.question.return_value = mock_msgbox.StandardButton.Yes

                gui.delete_stratagem()

                # Binding should be updated
                self.assertEqual(gui.bindings["insert"], "Unassigned")

            gui.close()

    def test_change_binding(self):
        """Test changing a macro binding."""
        with patch.object(MacroGUI, 'start_listener'):
            gui = MacroGUI(self.mock_listener)

            with patch('gui_qt.StratagemDialog') as mock_dialog, \
                 patch.object(gui, 'save_bindings'):
                mock_dialog.return_value.get_selected.return_value = "Mission - Reinforce"

                gui.change_binding("insert")

                self.assertEqual(gui.bindings["insert"], "Mission - Reinforce")

            gui.close()

    def test_filter_stratagems(self):
        """Test stratagem filtering."""
        with patch.object(MacroGUI, 'start_listener'):
            gui = MacroGUI(self.mock_listener)

            with patch.object(gui, 'populate_stratagem_list') as mock_populate:
                gui.filter_stratagems("mission")
                mock_populate.assert_called_with("mission")

            gui.close()


@unittest.skipIf(not PYQT_AVAILABLE, "PyQt6 not available")
class TestMacroKeyWidget(unittest.TestCase):
    """Test cases for MacroKeyWidget."""

    @classmethod
    def setUpClass(cls):
        """Create QApplication instance."""
        if PYQT_AVAILABLE and not QApplication.instance():
            cls.app = QApplication(sys.argv)
        else:
            cls.app = QApplication.instance()

    def test_widget_creation(self):
        """Test creating a macro key widget."""
        widget = MacroKeyWidget("insert", "Test Stratagem")

        self.assertEqual(widget.key_name, "insert")
        self.assertEqual(widget.stratagem_name, "Test Stratagem")

    def test_widget_update(self):
        """Test updating widget stratagem."""
        widget = MacroKeyWidget("insert", "Old Stratagem")
        widget.update_stratagem("New Stratagem")

        self.assertEqual(widget.stratagem_name, "New Stratagem")
        self.assertEqual(widget.stratagem_label.text(), "New Stratagem")

    def test_widget_click_signal(self):
        """Test that clicking widget emits signal."""
        widget = MacroKeyWidget("insert", "Test")

        signal_emitted = []

        def on_clicked(key):
            signal_emitted.append(key)

        widget.clicked.connect(on_clicked)

        # Simulate click
        QTest.mouseClick(widget, Qt.MouseButton.LeftButton)

        self.assertEqual(signal_emitted, ["insert"])


@unittest.skipIf(not PYQT_AVAILABLE, "PyQt6 not available")
class TestDialogsPyQt(unittest.TestCase):
    """Test custom dialog classes for PyQt6."""

    @classmethod
    def setUpClass(cls):
        """Create QApplication instance."""
        if PYQT_AVAILABLE and not QApplication.instance():
            cls.app = QApplication(sys.argv)
        else:
            cls.app = QApplication.instance()

    def test_stratagem_dialog_creation(self):
        """Test creating stratagem selection dialog."""
        stratagems = ["Test 1", "Test 2"]
        dialog = StratagemDialog(stratagems)

        self.assertIsNotNone(dialog)
        self.assertEqual(dialog.combo.count(), 2)

    def test_stratagem_dialog_empty_list(self):
        """Test dialog with empty list."""
        dialog = StratagemDialog([])
        self.assertEqual(dialog.combo.count(), 0)

    def test_add_stratagem_dialog_creation(self):
        """Test creating add stratagem dialog."""
        dialog = AddStratagemDialog()

        self.assertIsNotNone(dialog)
        self.assertIsNotNone(dialog.name_edit)
        self.assertIsNotNone(dialog.keys_edit)


@unittest.skipIf(not PYQT_AVAILABLE, "PyQt6 not available")
class TestPyQtIntegration(unittest.TestCase):
    """Integration tests for PyQt6 GUI workflows."""

    @classmethod
    def setUpClass(cls):
        """Create QApplication instance."""
        if PYQT_AVAILABLE and not QApplication.instance():
            cls.app = QApplication(sys.argv)
        else:
            cls.app = QApplication.instance()

    def setUp(self):
        """Set up test fixtures."""
        self.mock_listener = Mock()
        self.mock_listener.stratagems = {"Test": ["i"]}
        self.mock_listener.bindings = {"insert": "Test"}

        self.test_dir = tempfile.mkdtemp()
        self.mock_listener.stratagems_file = os.path.join(self.test_dir, "stratagems.json")
        self.mock_listener.macro_file = os.path.join(self.test_dir, "macros.json")
        self.mock_listener.running = False

    def tearDown(self):
        """Clean up."""
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

    @patch('gui_qt.QMessageBox')
    def test_full_workflow(self, mock_msgbox):
        """Test complete add-edit-delete workflow."""
        with patch.object(MacroGUI, 'start_listener'):
            gui = MacroGUI(self.mock_listener)

            # Add
            with patch('gui_qt.AddStratagemDialog') as mock_add_dialog, \
                 patch.object(gui, 'save_stratagems'), \
                 patch.object(gui, 'populate_stratagem_list'):
                mock_add_dialog.return_value.get_data.return_value = ("Workflow", "ijkl")

                gui.add_stratagem()
                self.assertIn("Workflow", gui.stratagems)

            # Edit
            with patch('gui_qt.StratagemDialog') as mock_select_dialog, \
                 patch('gui_qt.AddStratagemDialog') as mock_edit_dialog, \
                 patch.object(gui, 'save_stratagems'), \
                 patch.object(gui, 'populate_stratagem_list'):
                mock_select_dialog.return_value.get_selected.return_value = "Workflow"
                mock_edit_dialog.return_value.get_data.return_value = ("Workflow", "lkji")

                gui.edit_stratagem()
                self.assertEqual(gui.stratagems["Workflow"], ['l', 'k', 'j', 'i'])

            # Delete
            with patch('gui_qt.StratagemDialog') as mock_dialog, \
                 patch.object(gui, 'save_stratagems'), \
                 patch.object(gui, 'populate_stratagem_list'):
                mock_dialog.return_value.get_selected.return_value = "Workflow"
                mock_msgbox.question.return_value = mock_msgbox.StandardButton.Yes

                gui.delete_stratagem()
                self.assertNotIn("Workflow", gui.stratagems)

            gui.close()


@unittest.skipIf(not PYQT_AVAILABLE, "PyQt6 not available")
class TestConstants(unittest.TestCase):
    """Test that constants are properly defined."""

    def test_valid_keys_constant(self):
        """Test VALID_STRATAGEM_KEYS constant."""
        self.assertEqual(VALID_STRATAGEM_KEYS, {'i', 'j', 'k', 'l'})

    def test_colors_constant(self):
        """Test COLORS constant is defined."""
        self.assertIsInstance(COLORS, dict)
        self.assertIn('bg_dark', COLORS)
        self.assertIn('accent', COLORS)


if __name__ == '__main__':
    unittest.main()
