"""
Helldivers 2 Stratagem Macro Manager - GUI Module

This module provides a graphical user interface for managing stratagem macros
and key bindings for the Helldivers 2 game. It allows users to create, edit,
and delete stratagems, as well as bind them to macro keys.
"""

import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
import json
import threading
from listener import KeyboardListener
import os
import logging
from typing import Dict, List, Optional
import shutil
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('stratagems.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Constants
VALID_STRATAGEM_KEYS = {'i', 'j', 'k', 'l'}
BACKUP_DIR = 'backups'

# GUI class
class MacroGUI:
    """
    Main GUI application for managing Helldivers 2 stratagem macros.

    This class provides a Tkinter-based interface for:
    - Viewing and changing macro key bindings
    - Adding, editing, and deleting stratagems
    - Managing stratagem configurations

    Attributes:
        master: The root Tkinter window
        listener: KeyboardListener instance for handling macro execution
        stratagems: Dictionary of stratagem names to key sequences
        bindings: Dictionary of macro keys to stratagem names
    """
    def __init__(self, master: tk.Tk, listener: KeyboardListener) -> None:
        """
        Initialize the MacroGUI application.

        Args:
            master: The root Tkinter window
            listener: KeyboardListener instance for handling macro execution
        """
        self.master = master
        self.listener = listener
        self.master.title("Helldivers 2 - Stratagem Macro Manager")

        # Make window resizable
        self.master.resizable(True, True)

        # Create backup directory if it doesn't exist
        os.makedirs(BACKUP_DIR, exist_ok=True)

        # Store label references for efficient updates
        self.label_widgets: Dict[str, ttk.Label] = {}

        # Status bar variable
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")

        self.load_data()        # Load stratagems and bindings into the GUI
        self.create_widgets()   # Create widgets for each macro binding
        self.start_listener()   # Start the keyboard listener in a separate thread

        # Bind window close event
        self.master.protocol("WM_DELETE_WINDOW", self.on_close)

        # Setup keyboard shortcuts
        self.setup_keyboard_shortcuts()

        logger.info("GUI initialized successfully")

    def load_data(self) -> None:
        """Load stratagems and bindings from the listener."""
        self.stratagems = self.listener.stratagems
        self.bindings = self.listener.bindings
        logger.info(f"Loaded {len(self.stratagems)} stratagems and {len(self.bindings)} bindings")

    def validate_stratagem_keys(self, keys: str) -> tuple[bool, str]:
        """
        Validate that stratagem keys contain only valid characters.

        Args:
            keys: String of keys to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not keys:
            return False, "Stratagem sequence cannot be empty!"

        keys = keys.strip()
        if not keys:
            return False, "Stratagem sequence cannot be empty!"

        invalid_keys = [k for k in keys if k not in VALID_STRATAGEM_KEYS]
        if invalid_keys:
            return False, f"Invalid keys: {', '.join(invalid_keys)}\nOnly 'i', 'j', 'k', 'l' are allowed (Up, Left, Down, Right)"

        return True, ""

    def backup_file(self, file_path: str) -> None:
        """
        Create a backup of a file before modifying it.

        Args:
            file_path: Path to the file to backup
        """
        if os.path.exists(file_path):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.basename(file_path)
            backup_path = os.path.join(BACKUP_DIR, f"{filename}.{timestamp}.backup")
            try:
                shutil.copy2(file_path, backup_path)
                logger.info(f"Created backup: {backup_path}")
            except Exception as e:
                logger.error(f"Failed to create backup: {e}")

    def update_status(self, message: str) -> None:
        """
        Update the status bar with a message.

        Args:
            message: Status message to display
        """
        self.status_var.set(message)
        logger.info(f"Status: {message}")

    def setup_keyboard_shortcuts(self) -> None:
        """Setup keyboard shortcuts for the application."""
        self.master.bind('<Control-s>', lambda e: self.save_all())
        self.master.bind('<Control-q>', lambda e: self.on_close())
        logger.info("Keyboard shortcuts configured")

    def save_all(self) -> None:
        """Save both stratagems and bindings."""
        self.save_stratagems()
        self.save_bindings()
        self.update_status("All changes saved successfully")
        messagebox.showinfo("Saved", "All changes saved successfully!")

    def create_widgets(self) -> None:
        """Create and layout all GUI widgets."""
        row = 0
        cell_width = 100  # Set the static size for each cell width
        num_columns = 3  # Number of columns in your grid
    
        style = ttk.Style()
        style.configure('W.TButton', font=('default', 20))
    
        # Create a frame for the headers
        header_frame = ttk.Frame(self.master, borderwidth=2, relief="solid")
        header_frame.grid(row=row, columnspan=num_columns, padx=10, pady=5, sticky="nsew")

        # Display text to the user
        ttk.Label(header_frame, text="Stratagem -> Left Control", font=("default", 16)).grid(row=row, column=1, padx=10, pady=5, sticky="w")
        row += 1
        ttk.Label(header_frame, text="Stratagem Up -> i", font=("default", 16)).grid(row=row, column=1, padx=10, pady=5, sticky="w")
        row += 1
        ttk.Label(header_frame, text="Stratagem Left -> j", font=("default", 16)).grid(row=row, column=0, padx=10, pady=5, sticky="w")
        ttk.Label(header_frame, text="Stratagem Down -> k", font=("default", 16)).grid(row=row, column=1, padx=10, pady=5, sticky="w")
        ttk.Label(header_frame, text="Stratagem Right -> l", font=("default", 16)).grid(row=row, column=2, padx=10, pady=5, sticky="w")
        row += 1
    
        # Create headers
        headers = ["Macro Key", "Bound To", ""]
        for i in range(num_columns):
            ttk.Label(header_frame, text=headers[i], font=("default", 24, "bold")).grid(row=row, column=i, padx=10, pady=5, sticky="w")
            header_frame.columnconfigure(i, minsize=cell_width)
        row += 1
    
        # Create a frame for the data
        data_frame = ttk.Frame(self.master, borderwidth=2, relief="solid")
        data_frame.grid(row=row, columnspan=num_columns, padx=10, pady=5, sticky="nsew")
    
        # Create keybinding rows
        for key, stratagem_name in self.bindings.items():
            ttk.Label(data_frame, text=f"{key.capitalize()}", font=("default", 24, "bold")).grid(row=row, column=0, padx=10, pady=5, sticky="w")
            current_stratagem = ttk.Label(data_frame, text=stratagem_name, font=("default", 20, "italic"))
            current_stratagem.grid(row=row, column=1, padx=10, pady=5, sticky="w")

            # Store label reference for efficient updates
            self.label_widgets[key] = current_stratagem

            change_button = ttk.Button(data_frame, text="Change", style='W.TButton',
                                       command=lambda key=key, label=current_stratagem: self.change_binding(key, label))
            change_button.grid(row=row, column=2, padx=10, pady=5, sticky="w")
            data_frame.columnconfigure(i, minsize=cell_width)
            row += 1

        # Add buttons to the bottom of the GUI
        button_frame = ttk.Frame(self.master)
        button_frame.grid(row=row, columnspan=num_columns, padx=30, pady=5, sticky="nsew")
        ttk.Button(button_frame, text="Add Stratagem", style='W.TButton', command=self.add_stratagem).grid(row=0, column=0, padx=10, pady=5)
        ttk.Button(button_frame, text="Edit Stratagem", style='W.TButton', command=self.edit_stratagem).grid(row=0, column=1, padx=10, pady=5)
        ttk.Button(button_frame, text="Delete Stratagem", style='W.TButton', command=self.delete_stratagem).grid(row=0, column=2, padx=10, pady=5)
        row += 1

        # Add status bar at the bottom
        status_bar = ttk.Label(self.master, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=row, column=0, columnspan=num_columns, sticky="ew", padx=5, pady=5)

        # Configure grid weights for resizing
        self.master.grid_rowconfigure(row, weight=0)  # Status bar doesn't expand
        self.master.grid_columnconfigure(0, weight=1)
        self.master.grid_columnconfigure(1, weight=1)
        self.master.grid_columnconfigure(2, weight=1)

    def change_binding(self, key: str, label_widget: ttk.Label) -> None:
        """
        Open dialog to change the binding for a macro key.

        Args:
            key: The macro key to rebind
            label_widget: The label widget displaying the current binding
        """
        popup = tk.Toplevel(self.master)
        popup.title("Select Stratagem")

        # Create a variable to hold the selection
        new_stratagem = tk.StringVar(popup)
        new_stratagem.set(label_widget.cget("text"))

        # Create the option menu and position it
        choices = list(self.stratagems.keys())
        popup_menu = ttk.OptionMenu(
            popup, new_stratagem, new_stratagem.get(), *choices)
        popup_menu.pack(pady=20, padx=50)

        # Function to call when selection changes
        def on_selection(name, index, mode):
            self.update_binding(key, new_stratagem.get(), label_widget)
            popup.destroy()  # Close the popup after selection

        # Set the command to run on selection
        new_stratagem.trace_add("write", on_selection)

    def update_binding(self, key: str, new_stratagem: str, label_widget: ttk.Label) -> None:
        """
        Update the binding for a macro key.

        Args:
            key: The macro key to update
            new_stratagem: The new stratagem to bind
            label_widget: The label widget to update
        """
        self.bindings[key] = new_stratagem
        label_widget.config(text=new_stratagem)
        self.save_bindings()
        self.update_status(f"Bound '{key}' to '{new_stratagem}'")
        logger.info(f"Updated binding: {key} -> {new_stratagem}")

    def start_listener(self) -> None:
        """Start the keyboard listener in a separate daemon thread."""
        self.listener_thread = threading.Thread(target=self.listener.start)
        self.listener_thread.daemon = True
        self.listener_thread.start()
        logger.info("Keyboard listener thread started")

    def on_close(self) -> None:
        """Handle window close event - cleanup and exit."""
        logger.info("Closing application")
        if self.listener.running:
            self.listener.stop()  # Stop the listener if it is running
        self.master.destroy()  # Destroy the window

    def save_stratagems(self) -> None:
        """Save the stratagems to a JSON file with error handling and backup."""
        try:
            # Create backup before saving
            self.backup_file(self.listener.stratagems_file)

            with open(self.listener.stratagems_file, 'w') as file:
                json.dump(self.stratagems, file, sort_keys=True, indent=2)

            logger.info(f"Saved {len(self.stratagems)} stratagems to {self.listener.stratagems_file}")
        except PermissionError:
            error_msg = f"Permission denied: Cannot write to {self.listener.stratagems_file}"
            logger.error(error_msg)
            messagebox.showerror("Permission Error", error_msg)
        except OSError as e:
            error_msg = f"Failed to save stratagems: {e}"
            logger.error(error_msg)
            messagebox.showerror("Save Error", error_msg)

    def save_bindings(self) -> None:
        """Save the bindings to a JSON file with error handling and backup."""
        try:
            # Create backup before saving
            self.backup_file(self.listener.macro_file)

            with open(self.listener.macro_file, 'w') as file:
                json.dump(self.bindings, file, sort_keys=False, indent=2)

            logger.info(f"Saved {len(self.bindings)} bindings to {self.listener.macro_file}")
        except PermissionError:
            error_msg = f"Permission denied: Cannot write to {self.listener.macro_file}"
            logger.error(error_msg)
            messagebox.showerror("Permission Error", error_msg)
        except OSError as e:
            error_msg = f"Failed to save bindings: {e}"
            logger.error(error_msg)
            messagebox.showerror("Save Error", error_msg)
    
    def add_stratagem(self) -> None:
        """Add a new stratagem with validation."""
        # Open a dialog to let the user input the name of the new stratagem
        stratagem_name = CustomDialog(self.master, "Stratagem Name").result
        if not stratagem_name:
            return

        stratagem_name = stratagem_name.strip()
        if not stratagem_name:
            messagebox.showwarning("Warning", "Stratagem name cannot be empty!")
            return

        lower_case_stratagem_name = stratagem_name.lower()
        if any(existing_name.lower() == lower_case_stratagem_name for existing_name in self.stratagems):
            messagebox.showwarning("Warning", "Stratagem already exists!")
            return

        # Open a dialog to let the user input the keys of the new stratagem
        stratagem_keys = CustomDialog(self.master, "Stratagem Keys (i,j,k,l)").result
        if not stratagem_keys:
            return

        # Validate stratagem keys
        is_valid, error_msg = self.validate_stratagem_keys(stratagem_keys)
        if not is_valid:
            messagebox.showerror("Invalid Keys", error_msg)
            return

        self.stratagems[stratagem_name] = list(stratagem_keys.strip())
        self.save_stratagems()
        self.update_status(f"Added stratagem '{stratagem_name}'")
        messagebox.showinfo("Success", f"Stratagem '{stratagem_name}' added successfully!")
        logger.info(f"Added new stratagem: {stratagem_name} -> {list(stratagem_keys)}")

    def edit_stratagem(self) -> None:
        """Edit an existing stratagem with validation."""
        if not self.stratagems:
            messagebox.showwarning("Warning", "No stratagems available to edit!")
            return

        # Open a dialog to let the user select the stratagem to edit
        dialog = ComboDialog(self.master, stratagems=list(self.stratagems.keys()))
        stratagem_name = dialog.result
        if not stratagem_name or stratagem_name not in self.stratagems:
            return

        # Open a dialog to let the user input the new keys for the stratagem
        current_keys = ''.join(self.stratagems[stratagem_name])
        stratagem_keys = CustomDialog(self.master, f"Edit '{stratagem_name}' (current: {current_keys})").result
        if not stratagem_keys:
            return

        # Validate stratagem keys
        is_valid, error_msg = self.validate_stratagem_keys(stratagem_keys)
        if not is_valid:
            messagebox.showerror("Invalid Keys", error_msg)
            return

        self.stratagems[stratagem_name] = list(stratagem_keys.strip())
        self.save_stratagems()
        self.update_status(f"Updated stratagem '{stratagem_name}'")
        messagebox.showinfo("Success", f"Stratagem '{stratagem_name}' updated successfully!")
        logger.info(f"Edited stratagem: {stratagem_name} -> {list(stratagem_keys)}")

    def delete_stratagem(self) -> None:
        """Delete an existing stratagem with confirmation."""
        if not self.stratagems:
            messagebox.showwarning("Warning", "No stratagems available to delete!")
            return

        # Open a dialog to let the user select the stratagem to delete
        dialog = ComboDialog(self.master, stratagems=list(self.stratagems.keys()))
        stratagem_name = dialog.result
        if not stratagem_name or stratagem_name not in self.stratagems:
            return

        # Confirm deletion
        confirm = messagebox.askyesno(
            "Confirm Deletion",
            f"Are you sure you want to delete '{stratagem_name}'?\n\nThis action cannot be undone."
        )
        if not confirm:
            return

        del self.stratagems[stratagem_name]
        self.save_stratagems()

        # Check if the deleted stratagem is bound to any button
        for key, bound_stratagem in list(self.bindings.items()):
            if bound_stratagem == stratagem_name:
                # If it is, update the stratagem name in the bindings dictionary to "Unassigned"
                self.bindings[key] = "Unassigned"
                self.save_bindings()
                # Use cached label reference for efficient update
                if key in self.label_widgets:
                    self.label_widgets[key].config(text="Unassigned")

        self.update_status(f"Deleted stratagem '{stratagem_name}'")
        messagebox.showinfo("Success", f"Stratagem '{stratagem_name}' deleted successfully!")
        logger.info(f"Deleted stratagem: {stratagem_name}") 

class ComboDialog(simpledialog.Dialog):
    """
    Custom dialog for selecting from a dropdown list of stratagems.

    Attributes:
        stratagems: List of stratagem names to display in the dropdown
        result: The selected stratagem name
    """
    def __init__(self, parent: tk.Tk, title: Optional[str] = None, stratagems: Optional[List[str]] = None):
        """
        Initialize the combo dialog.

        Args:
            parent: Parent window
            title: Dialog title
            stratagems: List of stratagem names
        """
        self.stratagems = stratagems if stratagems else []
        super().__init__(parent, title=title)

    def body(self, master: tk.Frame) -> ttk.Combobox:
        """
        Create the dialog body.

        Args:
            master: Parent frame

        Returns:
            The combobox widget for initial focus
        """
        self.title("Select a Stratagem")
        tk.Label(master, text="Name:").grid(row=0)
        self.combo = ttk.Combobox(master, values=self.stratagems, width=40)
        self.combo.grid(row=0, column=1, padx=5, pady=5)
        self.combo.focus_set()  # Set focus to the combobox
        return self.combo  # initial focus

    def apply(self) -> None:
        """Store the selected value."""
        self.result = self.combo.get()

class CustomDialog(tk.simpledialog.Dialog):
    """
    Custom dialog for text input.

    Attributes:
        result: The entered text value
    """
    def body(self, master: tk.Frame) -> tk.Entry:
        """
        Create the dialog body.

        Args:
            master: Parent frame

        Returns:
            The entry widget for initial focus
        """
        self.entry = tk.Entry(master, width=40)
        self.entry.pack(padx=10, pady=10)
        self.entry.focus_set()  # Set focus to the entry
        return self.entry  # initial focus

    def apply(self) -> None:
        """Store the entered value."""
        self.result = self.entry.get()

# Main function
if __name__ == "__main__":
    mainApplication = tk.Tk()
    # Get the directory of the script
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Specify the file paths relative to the script directory
    stratagems_file = os.path.join(script_dir, 'stratagems.json')
    macros_file = os.path.join(script_dir, 'macros.json')

    # Create the KeyboardListener instance
    listener = KeyboardListener(stratagems_file, macros_file)
    app = MacroGUI(mainApplication, listener)
    mainApplication.mainloop()
