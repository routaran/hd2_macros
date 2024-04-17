import tkinter as tk
from tkinter import ttk, simpledialog
import json
import threading
from listener import KeyboardListener

# GUI class
class MacroGUI:
    # Constructor
    def __init__(self, master, listener):
        self.master = master
        self.listener = listener
        self.master.title("Macro Editor")

        self.load_data()        # Load stratagems and bindings into the GUI
        self.create_widgets()   # Create widgets for each macro binding
        self.start_listener()   # Start the keyboard listener in a separate thread

        # Bind window close event
        self.master.protocol("WM_DELETE_WINDOW", self.on_close) # Bind the window close event to the on_close method

    # Load stratagems and bindings into the GUI
    def load_data(self):
        self.stratagems = self.listener.stratagems
        self.bindings = self.listener.bindings

    # Create widgets for each macro binding
    def create_widgets(self):
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

    # Change the binding of a key
    def change_binding(self, key, label_widget):
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

    # Update the binding of a key
    def update_binding(self, key, new_stratagem, label_widget):
        self.bindings[key] = new_stratagem
        label_widget.config(text=new_stratagem)
        self.save_bindings()

    # Start the listener in a separate thread
    def start_listener(self):
        self.listener_thread = threading.Thread(target=self.listener.start)
        self.listener_thread.daemon = True
        self.listener_thread.start()

    # Close the window
    def on_close(self):
        if self.listener.running:
            self.listener.stop()  # Stop the listener if it is running
        self.master.destroy()  # Destroy the window

    # Save the stratagems to a JSON file
    def save_stratagems(self):
        with open(self.listener.stratagems_file, 'w') as file:
            json.dump(self.stratagems, file, sort_keys=True)

    # Save the bindings to a JSON file
    def save_bindings(self):
        with open(self.listener.macro_file, 'w') as file:
            json.dump(self.bindings, file, sort_keys=False)
    
    # Add a new stratagem
    def add_stratagem(self):
        # Open a dialog to let the user input the name of the new stratagem
        stratagem_name = CustomDialog(self.master, "Stratagem Name").result
        if stratagem_name:
            lower_case_stratagem_name = stratagem_name.lower()
            if any(existing_name.lower() == lower_case_stratagem_name for existing_name in self.stratagems):
                tk.messagebox.showwarning("Warning", "Stratagem already exists!")
            else:
                # Open a dialog to let the user input the keys of the new stratagem
                stratagem_keys = CustomDialog(self.master, "Stratagem Keys").result
                if stratagem_keys:
                    self.stratagems[stratagem_name] = list(stratagem_keys)
                    self.save_stratagems()

    # Edit an existing stratagem
    def edit_stratagem(self):
        # Open a dialog to let the user select the stratagem to edit
        dialog = ComboDialog(self.master, stratagems=list(self.stratagems.keys()))
        stratagem_name = dialog.result
        if stratagem_name in self.stratagems:
            # Open a dialog to let the user input the new keys for the stratagem
            stratagem_keys = CustomDialog(self.master, "Edit a Stratagem").result
            if stratagem_keys:
                self.stratagems[stratagem_name] = list(stratagem_keys)
                self.save_stratagems()
        else:
            tk.messagebox.showwarning("Warning", "Stratagem does not exist!")

    # Delete an existing stratagem
    def delete_stratagem(self):
        # Open a dialog to let the user select the stratagem to delete
        dialog = ComboDialog(self.master, stratagems=list(self.stratagems.keys()))
        stratagem_name = dialog.result
        if stratagem_name in self.stratagems:
            del self.stratagems[stratagem_name]
            self.save_stratagems()
    
            # Check if the deleted stratagem is bound to any button
            for key, bound_stratagem in list(self.bindings.items()):
                if bound_stratagem == stratagem_name:
                    # If it is, update the stratagem name in the bindings dictionary to "Unassigned"
                    self.bindings[key] = "Unassigned"                    
                    self.save_bindings()
                    self.update_view(stratagem_name)
        else:
            tk.messagebox.showwarning("Warning", "Stratagem does not exist!")   
    
    # Update the view when a stratagem is deleted
    def update_view(self, stratagem_name):
        # Find the label of the button that is bound to the deleted stratagem
        for child in self.master.winfo_children():
            if isinstance(child, ttk.Frame):
                for grandchild in child.winfo_children():
                    if isinstance(grandchild, ttk.Label) and grandchild.cget("text") == stratagem_name:
                        # Update the label of the button
                        grandchild.config(text="Unassigned")
                        break 

# Custom dialog classes
class ComboDialog(simpledialog.Dialog):
    def __init__(self, parent, title=None, stratagems=None):
        self.stratagems = stratagems
        super().__init__(parent, title=title)

    def body(self, master):
        self.title("Edit a Stratagem")
        tk.Label(master, text="Name:").grid(row=0)
        self.combo = ttk.Combobox(master, values=self.stratagems)
        self.combo.grid(row=0, column=1)
        self.combo.focus_set()  # Set focus to the combobox
        return self.combo  # initial focus

    def apply(self):
        self.result = self.combo.get()

# Custom dialog classes
class CustomDialog(tk.simpledialog.Dialog):
    def body(self, master):
        self.entry = tk.Entry(master)
        self.entry.pack()
        self.entry.focus_set()  # Set focus to the entry
        return self.entry  # initial focus

    def apply(self):
        self.result = self.entry.get()

# Main function
if __name__ == "__main__":
    mainApplication = tk.Tk()
    listener = KeyboardListener('stratagems.json', 'macros.json')
    app = MacroGUI(mainApplication, listener)
    mainApplication.mainloop()
