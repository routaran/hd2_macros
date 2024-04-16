import tkinter as tk
from tkinter import ttk
import json
import threading
# Correcting the import based on your file structure
from listener import KeyboardListener


class MacroGUI:
    def __init__(self, master, listener):
        self.master = master
        self.listener = listener
        self.master.title("Macro Editor")

        self.load_data()
        self.create_widgets()
        self.start_listener()

        # Bind window close event
        self.master.protocol("WM_DELETE_WINDOW", self.on_close)

    def load_data(self):
        """Load strategems and bindings into the GUI."""
        self.strategems = self.listener.strategems
        self.bindings = self.listener.bindings

    def create_widgets(self):
        """Create widgets for each macro binding."""
        row = 0
        for key, strategem_name in self.bindings.items():
            ttk.Label(self.master, text=f"Key: {key}").grid(row=row, column=0)
            current_strategem = ttk.Label(self.master, text=strategem_name)
            current_strategem.grid(row=row, column=1)
            change_button = ttk.Button(self.master, text="Change",
                                       command=lambda key=key, label=current_strategem: self.change_binding(key, label))
            change_button.grid(row=row, column=2)
            row += 1


    def change_binding(self, key, label_widget):
        """Change the binding of a key using a popup window."""
        popup = tk.Toplevel(self.master)
        popup.title("Select Strategem")
        popup.geometry("300x100")  # Adjust size as necessary

        # Create a variable to hold the selection
        new_strategem = tk.StringVar(popup)
        new_strategem.set(label_widget.cget("text"))

        # Create the option menu and position it
        choices = list(self.strategems.keys())
        popup_menu = ttk.OptionMenu(
            popup, new_strategem, new_strategem.get(), *choices)
        popup_menu.pack(pady=20, padx=50)

        # Function to call when selection changes
        def on_selection(name, index, mode):
            self.update_binding(key, new_strategem.get(), label_widget)
            popup.destroy()  # Close the popup after selection

        # Set the command to run on selection
        new_strategem.trace("w", on_selection)

    def update_binding(self, key, new_strategem, label_widget):
        """Update the binding of a key and refresh the GUI."""
        self.bindings[key] = new_strategem
        label_widget.config(text=new_strategem)
        self.save_bindings()

    def save_bindings(self):
        """Save the updated bindings back to the JSON file."""
        with open(self.listener.macro_file, 'w') as file:
            json.dump(self.bindings, file)

    def start_listener(self):
        """Start the keyboard listener in a separate thread."""
        self.listener_thread = threading.Thread(target=self.listener.start)
        # This makes the thread exit when the main program exits
        self.listener_thread.daemon = True
        self.listener_thread.start()

    def on_close(self):
        """Handle GUI closure."""
        if self.listener.running:
            self.listener.stop()  # Stop the listener if it is running
        self.master.destroy()  # Destroy the window

if __name__ == "__main__":
    root = tk.Tk()
    listener = KeyboardListener('strategems.json', 'macros.json')
    app = MacroGUI(root, listener)
    root.mainloop()
