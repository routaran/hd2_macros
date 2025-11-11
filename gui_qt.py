"""
Helldivers 2 Stratagem Macro Manager - PyQt6 GUI Module

Modern PyQt6-based graphical user interface with improved design,
dark theme, and enhanced user experience.
"""

import sys
import os
import json
import threading
import logging
from typing import Dict, List, Optional
from datetime import datetime
import shutil

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QListWidget, QFrame, QDialog,
    QDialogButtonBox, QComboBox, QMessageBox, QStatusBar, QSplitter,
    QGroupBox, QGridLayout, QSystemTrayIcon, QMenu, QScrollArea
)
from PyQt6.QtCore import Qt, QSize, pyqtSignal, QObject
from PyQt6.QtGui import QIcon, QFont, QPalette, QColor, QAction

from listener import KeyboardListener

# Setup logging
logger = logging.getLogger(__name__)

# Constants
VALID_STRATAGEM_KEYS = {'i', 'j', 'k', 'l'}
BACKUP_DIR = 'backups'

# Dark theme colors
COLORS = {
    'bg_dark': '#1e1e1e',
    'bg_medium': '#2d2d30',
    'bg_light': '#3e3e42',
    'accent': '#007acc',
    'accent_hover': '#005a9e',
    'text': '#cccccc',
    'text_dim': '#858585',
    'success': '#4ec9b0',
    'warning': '#ce9178',
    'error': '#f48771',
    'border': '#555555'
}

# Global dark theme stylesheet
DARK_THEME = f"""
QMainWindow {{
    background-color: {COLORS['bg_dark']};
    color: {COLORS['text']};
}}

QWidget {{
    background-color: {COLORS['bg_dark']};
    color: {COLORS['text']};
    font-size: 12px;
}}

QPushButton {{
    background-color: {COLORS['accent']};
    color: white;
    border: none;
    padding: 10px 20px;
    border-radius: 5px;
    font-size: 13px;
    font-weight: bold;
}}

QPushButton:hover {{
    background-color: {COLORS['accent_hover']};
}}

QPushButton:pressed {{
    background-color: #003d66;
}}

QPushButton:disabled {{
    background-color: {COLORS['bg_light']};
    color: {COLORS['text_dim']};
}}

QLineEdit {{
    background-color: {COLORS['bg_medium']};
    color: {COLORS['text']};
    border: 1px solid {COLORS['border']};
    padding: 8px;
    border-radius: 4px;
    font-size: 13px;
}}

QLineEdit:focus {{
    border: 1px solid {COLORS['accent']};
}}

QListWidget {{
    background-color: {COLORS['bg_medium']};
    color: {COLORS['text']};
    border: 1px solid {COLORS['border']};
    border-radius: 4px;
    padding: 5px;
}}

QListWidget::item {{
    padding: 8px;
    border-radius: 3px;
}}

QListWidget::item:selected {{
    background-color: {COLORS['accent']};
    color: white;
}}

QListWidget::item:hover {{
    background-color: {COLORS['bg_light']};
}}

QFrame {{
    background-color: {COLORS['bg_medium']};
    border: 1px solid {COLORS['border']};
    border-radius: 5px;
}}

QLabel {{
    color: {COLORS['text']};
}}

QStatusBar {{
    background-color: {COLORS['bg_medium']};
    color: {COLORS['text']};
    border-top: 1px solid {COLORS['border']};
}}

QComboBox {{
    background-color: {COLORS['bg_medium']};
    color: {COLORS['text']};
    border: 1px solid {COLORS['border']};
    padding: 5px;
    border-radius: 4px;
}}

QComboBox::drop-down {{
    border: none;
    width: 20px;
}}

QComboBox::down-arrow {{
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 5px solid {COLORS['text']};
}}

QComboBox QAbstractItemView {{
    background-color: {COLORS['bg_medium']};
    color: {COLORS['text']};
    selection-background-color: {COLORS['accent']};
    border: 1px solid {COLORS['border']};
}}

QGroupBox {{
    border: 1px solid {COLORS['border']};
    border-radius: 5px;
    margin-top: 10px;
    padding-top: 10px;
    font-weight: bold;
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 5px;
    color: {COLORS['accent']};
}}

QScrollArea {{
    border: none;
}}

QDialog {{
    background-color: {COLORS['bg_dark']};
}}
"""


class MacroKeyWidget(QFrame):
    """Widget representing a visual macro key button."""

    clicked = pyqtSignal(str)  # Emits the key name when clicked

    def __init__(self, key_name: str, stratagem_name: str, parent=None):
        super().__init__(parent)
        self.key_name = key_name
        self.stratagem_name = stratagem_name

        self.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Raised)
        self.setLineWidth(2)
        self.setMinimumSize(200, 100)
        self.setMaximumSize(250, 120)

        # Layout
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)

        # Key label (styled like keyboard key)
        self.key_label = QLabel(key_name.upper())
        self.key_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        key_font = QFont("Consolas", 16, QFont.Weight.Bold)
        self.key_label.setFont(key_font)
        self.key_label.setStyleSheet(f"""
            background-color: {COLORS['bg_light']};
            border: 2px solid {COLORS['border']};
            border-radius: 8px;
            padding: 15px;
            color: {COLORS['text']};
        """)

        # Stratagem label
        self.stratagem_label = QLabel(stratagem_name)
        self.stratagem_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.stratagem_label.setWordWrap(True)
        stratagem_font = QFont("Arial", 10)
        self.stratagem_label.setFont(stratagem_font)
        self.stratagem_label.setStyleSheet(f"color: {COLORS['text_dim']};")

        layout.addWidget(self.key_label)
        layout.addWidget(self.stratagem_label)

        self.setLayout(layout)

        # Make clickable
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def mousePressEvent(self, event):
        """Handle mouse click."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.key_name)

    def update_stratagem(self, stratagem_name: str):
        """Update the stratagem label."""
        self.stratagem_name = stratagem_name
        self.stratagem_label.setText(stratagem_name)

    def flash_success(self):
        """Flash green to indicate successful execution."""
        self.key_label.setStyleSheet(f"""
            background-color: {COLORS['success']};
            border: 2px solid {COLORS['border']};
            border-radius: 8px;
            padding: 15px;
            color: white;
        """)
        # Reset after 200ms
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(200, self.reset_style)

    def reset_style(self):
        """Reset to default style."""
        self.key_label.setStyleSheet(f"""
            background-color: {COLORS['bg_light']};
            border: 2px solid {COLORS['border']};
            border-radius: 8px;
            padding: 15px;
            color: {COLORS['text']};
        """)


class StratagemDialog(QDialog):
    """Dialog for selecting a stratagem."""

    def __init__(self, stratagems: List[str], title: str = "Select Stratagem", parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumWidth(400)

        layout = QVBoxLayout()

        # Label
        label = QLabel("Select a stratagem:")
        layout.addWidget(label)

        # Combo box
        self.combo = QComboBox()
        self.combo.addItems(stratagems)
        self.combo.setCurrentIndex(0)
        layout.addWidget(self.combo)

        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)

    def get_selected(self) -> Optional[str]:
        """Get the selected stratagem."""
        if self.exec() == QDialog.DialogCode.Accepted:
            return self.combo.currentText()
        return None


class AddStratagemDialog(QDialog):
    """Dialog for adding a new stratagem."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Stratagem")
        self.setMinimumWidth(400)

        layout = QVBoxLayout()

        # Name field
        name_label = QLabel("Stratagem Name:")
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("e.g., Mission - Reinforce")
        layout.addWidget(name_label)
        layout.addWidget(self.name_edit)

        # Keys field
        keys_label = QLabel("Keys (i, j, k, l only):")
        self.keys_edit = QLineEdit()
        self.keys_edit.setPlaceholderText("e.g., ikjli")
        layout.addWidget(keys_label)
        layout.addWidget(self.keys_edit)

        # Help text
        help_text = QLabel("i = Up, j = Left, k = Down, l = Right")
        help_text.setStyleSheet(f"color: {COLORS['text_dim']};")
        layout.addWidget(help_text)

        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)

    def get_data(self) -> Optional[tuple]:
        """Get the entered data."""
        if self.exec() == QDialog.DialogCode.Accepted:
            return (self.name_edit.text().strip(), self.keys_edit.text().strip())
        return None


class MacroGUI(QMainWindow):
    """Main PyQt6 GUI for Helldivers 2 Stratagem Macro Manager."""

    def __init__(self, listener: KeyboardListener):
        super().__init__()
        self.listener = listener
        self.stratagems = listener.stratagems
        self.bindings = listener.bindings
        self.macro_widgets: Dict[str, MacroKeyWidget] = {}

        # Create backup directory
        os.makedirs(BACKUP_DIR, exist_ok=True)

        # Setup UI
        self.init_ui()

        # Start listener
        self.start_listener()

        # Setup system tray
        self.setup_system_tray()

        logger.info("PyQt6 GUI initialized successfully")

    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("Helldivers 2 - Stratagem Macro Manager")
        self.setMinimumSize(1000, 700)

        # Apply dark theme
        self.setStyleSheet(DARK_THEME)

        # Central widget
        central_widget = QWidget()
        self.setCentral(central_widget)

        # Main layout
        main_layout = QHBoxLayout()

        # Left panel - Macro keys
        left_panel = self.create_macro_panel()
        main_layout.addWidget(left_panel, 2)

        # Right panel - Stratagem library
        right_panel = self.create_stratagem_panel()
        main_layout.addWidget(right_panel, 1)

        central_widget.setLayout(main_layout)

        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

        # Menu bar
        self.create_menu_bar()

    def create_menu_bar(self):
        """Create the menu bar."""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("File")

        save_action = QAction("Save All", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_all)
        file_menu.addAction(save_action)

        file_menu.addSeparator()

        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Help menu
        help_menu = menubar.addMenu("Help")

        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def create_macro_panel(self) -> QWidget:
        """Create the macro keys panel."""
        panel = QWidget()
        layout = QVBoxLayout()

        # Title
        title = QLabel("Macro Keys")
        title_font = QFont("Arial", 16, QFont.Weight.Bold)
        title.setFont(title_font)
        title.setStyleSheet(f"color: {COLORS['accent']};")
        layout.addWidget(title)

        # Info text
        info = QLabel("Click a key to change its binding")
        info.setStyleSheet(f"color: {COLORS['text_dim']};")
        layout.addWidget(info)

        # Scroll area for macro keys
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; }")

        scroll_widget = QWidget()
        grid = QGridLayout()
        grid.setSpacing(15)

        # Create macro key widgets in a grid
        row, col = 0, 0
        for key, stratagem_name in self.bindings.items():
            widget = MacroKeyWidget(key, stratagem_name)
            widget.clicked.connect(self.change_binding)
            self.macro_widgets[key] = widget

            grid.addWidget(widget, row, col)
            col += 1
            if col >= 3:  # 3 columns
                col = 0
                row += 1

        scroll_widget.setLayout(grid)
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)

        panel.setLayout(layout)
        return panel

    def create_stratagem_panel(self) -> QWidget:
        """Create the stratagem library panel."""
        panel = QWidget()
        layout = QVBoxLayout()

        # Title
        title = QLabel("Stratagem Library")
        title_font = QFont("Arial", 16, QFont.Weight.Bold)
        title.setFont(title_font)
        title.setStyleSheet(f"color: {COLORS['accent']};")
        layout.addWidget(title)

        # Search box
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search stratagems...")
        self.search_box.textChanged.connect(self.filter_stratagems)
        layout.addWidget(self.search_box)

        # Stratagem list
        self.stratagem_list = QListWidget()
        self.populate_stratagem_list()
        layout.addWidget(self.stratagem_list)

        # Buttons
        button_layout = QVBoxLayout()
        button_layout.setSpacing(10)

        add_btn = QPushButton("Add Stratagem")
        add_btn.clicked.connect(self.add_stratagem)
        button_layout.addWidget(add_btn)

        edit_btn = QPushButton("Edit Stratagem")
        edit_btn.clicked.connect(self.edit_stratagem)
        button_layout.addWidget(edit_btn)

        delete_btn = QPushButton("Delete Stratagem")
        delete_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['error']};
            }}
            QPushButton:hover {{
                background-color: #d16b5c;
            }}
        """)
        delete_btn.clicked.connect(self.delete_stratagem)
        button_layout.addWidget(delete_btn)

        layout.addLayout(button_layout)

        panel.setLayout(layout)
        return panel

    def populate_stratagem_list(self, filter_text: str = ""):
        """Populate the stratagem list."""
        self.stratagem_list.clear()
        for name, keys in sorted(self.stratagems.items()):
            if filter_text.lower() in name.lower():
                keys_str = ''.join(keys)
                self.stratagem_list.addItem(f"{name} ({keys_str})")

    def filter_stratagems(self, text: str):
        """Filter stratagems based on search text."""
        self.populate_stratagem_list(text)

    def change_binding(self, key: str):
        """Change the binding for a macro key."""
        dialog = StratagemDialog(list(self.stratagems.keys()), f"Bind to {key.upper()}", self)
        stratagem = dialog.get_selected()

        if stratagem:
            self.bindings[key] = stratagem
            self.macro_widgets[key].update_stratagem(stratagem)
            self.save_bindings()
            self.status_bar.showMessage(f"Bound '{key}' to '{stratagem}'", 3000)
            logger.info(f"Updated binding: {key} -> {stratagem}")

    def add_stratagem(self):
        """Add a new stratagem."""
        dialog = AddStratagemDialog(self)
        result = dialog.get_data()

        if not result:
            return

        name, keys = result

        if not name:
            QMessageBox.warning(self, "Warning", "Stratagem name cannot be empty!")
            return

        if any(existing.lower() == name.lower() for existing in self.stratagems):
            QMessageBox.warning(self, "Warning", "Stratagem already exists!")
            return

        is_valid, error_msg = self.validate_stratagem_keys(keys)
        if not is_valid:
            QMessageBox.critical(self, "Invalid Keys", error_msg)
            return

        self.stratagems[name] = list(keys)
        self.save_stratagems()
        self.populate_stratagem_list(self.search_box.text())
        self.status_bar.showMessage(f"Added stratagem '{name}'", 3000)
        QMessageBox.information(self, "Success", f"Stratagem '{name}' added successfully!")
        logger.info(f"Added new stratagem: {name} -> {list(keys)}")

    def edit_stratagem(self):
        """Edit an existing stratagem."""
        if not self.stratagems:
            QMessageBox.warning(self, "Warning", "No stratagems available to edit!")
            return

        # Select stratagem
        dialog = StratagemDialog(list(self.stratagems.keys()), "Select Stratagem to Edit", self)
        stratagem_name = dialog.get_selected()

        if not stratagem_name:
            return

        # Get new keys
        current_keys = ''.join(self.stratagems[stratagem_name])
        new_dialog = AddStratagemDialog(self)
        new_dialog.setWindowTitle(f"Edit '{stratagem_name}'")
        new_dialog.name_edit.setText(stratagem_name)
        new_dialog.name_edit.setEnabled(False)
        new_dialog.keys_edit.setText(current_keys)
        new_dialog.keys_edit.setPlaceholderText(f"Current: {current_keys}")

        result = new_dialog.get_data()
        if not result:
            return

        _, keys = result

        is_valid, error_msg = self.validate_stratagem_keys(keys)
        if not is_valid:
            QMessageBox.critical(self, "Invalid Keys", error_msg)
            return

        self.stratagems[stratagem_name] = list(keys)
        self.save_stratagems()
        self.populate_stratagem_list(self.search_box.text())
        self.status_bar.showMessage(f"Updated stratagem '{stratagem_name}'", 3000)
        QMessageBox.information(self, "Success", f"Stratagem '{stratagem_name}' updated successfully!")
        logger.info(f"Edited stratagem: {stratagem_name} -> {list(keys)}")

    def delete_stratagem(self):
        """Delete an existing stratagem."""
        if not self.stratagems:
            QMessageBox.warning(self, "Warning", "No stratagems available to delete!")
            return

        dialog = StratagemDialog(list(self.stratagems.keys()), "Select Stratagem to Delete", self)
        stratagem_name = dialog.get_selected()

        if not stratagem_name:
            return

        # Confirm deletion
        reply = QMessageBox.question(
            self,
            "Confirm Deletion",
            f"Are you sure you want to delete '{stratagem_name}'?\n\nThis action cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        del self.stratagems[stratagem_name]
        self.save_stratagems()

        # Update any bindings
        for key, bound_stratagem in list(self.bindings.items()):
            if bound_stratagem == stratagem_name:
                self.bindings[key] = "Unassigned"
                self.macro_widgets[key].update_stratagem("Unassigned")
                self.save_bindings()

        self.populate_stratagem_list(self.search_box.text())
        self.status_bar.showMessage(f"Deleted stratagem '{stratagem_name}'", 3000)
        QMessageBox.information(self, "Success", f"Stratagem '{stratagem_name}' deleted successfully!")
        logger.info(f"Deleted stratagem: {stratagem_name}")

    def validate_stratagem_keys(self, keys: str) -> tuple[bool, str]:
        """Validate stratagem keys."""
        if not keys:
            return False, "Stratagem sequence cannot be empty!"

        keys = keys.strip()
        if not keys:
            return False, "Stratagem sequence cannot be empty!"

        invalid_keys = [k for k in keys if k not in VALID_STRATAGEM_KEYS]
        if invalid_keys:
            return False, f"Invalid keys: {', '.join(invalid_keys)}\nOnly 'i', 'j', 'k', 'l' are allowed (Up, Left, Down, Right)"

        return True, ""

    def backup_file(self, file_path: str):
        """Create a backup of a file."""
        if os.path.exists(file_path):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.basename(file_path)
            backup_path = os.path.join(BACKUP_DIR, f"{filename}.{timestamp}.backup")
            try:
                shutil.copy2(file_path, backup_path)
                logger.info(f"Created backup: {backup_path}")
            except Exception as e:
                logger.error(f"Failed to create backup: {e}")

    def save_stratagems(self):
        """Save stratagems to file."""
        try:
            self.backup_file(self.listener.stratagems_file)
            with open(self.listener.stratagems_file, 'w') as file:
                json.dump(self.stratagems, file, sort_keys=True, indent=2)
            logger.info(f"Saved {len(self.stratagems)} stratagems")
        except Exception as e:
            logger.error(f"Failed to save stratagems: {e}")
            QMessageBox.critical(self, "Save Error", f"Failed to save stratagems: {e}")

    def save_bindings(self):
        """Save bindings to file."""
        try:
            self.backup_file(self.listener.macro_file)
            with open(self.listener.macro_file, 'w') as file:
                json.dump(self.bindings, file, sort_keys=False, indent=2)
            logger.info(f"Saved {len(self.bindings)} bindings")
        except Exception as e:
            logger.error(f"Failed to save bindings: {e}")
            QMessageBox.critical(self, "Save Error", f"Failed to save bindings: {e}")

    def save_all(self):
        """Save both stratagems and bindings."""
        self.save_stratagems()
        self.save_bindings()
        self.status_bar.showMessage("All changes saved successfully", 3000)
        QMessageBox.information(self, "Saved", "All changes saved successfully!")

    def start_listener(self):
        """Start the keyboard listener in a separate thread."""
        self.listener_thread = threading.Thread(target=self.listener.start)
        self.listener_thread.daemon = True
        self.listener_thread.start()
        logger.info("Keyboard listener thread started")

    def setup_system_tray(self):
        """Setup system tray icon."""
        # Note: This requires an icon file
        # For now, we'll skip the icon part
        pass

    def show_about(self):
        """Show about dialog."""
        QMessageBox.about(
            self,
            "About HD2 Macro Manager",
            "Helldivers 2 Stratagem Macro Manager\n\n"
            "Version 2.0.0 with PyQt6 UI\n\n"
            "A modern, professional macro manager for Helldivers 2.\n\n"
            "Built with Python and PyQt6"
        )

    def closeEvent(self, event):
        """Handle window close event."""
        logger.info("Closing application")
        if self.listener.running:
            self.listener.stop()
        event.accept()


def main():
    """Main entry point for PyQt6 GUI."""
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('stratagems.log'),
            logging.StreamHandler()
        ]
    )

    # Get file paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    stratagems_file = os.path.join(script_dir, 'stratagems.json')
    macros_file = os.path.join(script_dir, 'macros.json')

    # Create listener
    listener = KeyboardListener(stratagems_file, macros_file)

    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName("HD2 Macro Manager")

    # Create and show main window
    window = MacroGUI(listener)
    window.show()

    # Run application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
