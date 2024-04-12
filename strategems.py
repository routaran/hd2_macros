from pynput.keyboard import Key, Controller, Listener
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QInputDialog, QGridLayout, QFrame, QMessageBox, QGroupBox
import time, threading, json, os
from PyQt5.QtCore import Qt
from datetime import datetime

# Get the directory of the script
dir_path = os.path.dirname(os.path.realpath(__file__))
# Construct the paths to the JSON files
strategems_path = os.path.join(dir_path, './strategems.json')
macros_path = os.path.join(dir_path, './macros.json')

# Create keyboard controller object
keyboard = Controller()

# Variable to track of the state of the macro listener
running = False

# Load strategems from a JSON file
try:
    with open(strategems_path, 'r') as f:
        strategems = json.load(f)# Ensure 'Unassigned' is a key in strategems
        if 'Unassigned' not in strategems:
            strategems['Unassigned'] = []
        # Order the strategems dictionary by key in ascending order
        strategems = dict(sorted(strategems.items()))
except FileNotFoundError as e:
    print(f"FileNotFoundError: {e}")
    strategems = {}  # Initialize an empty dictionary if the file does not exist
    strategems['Unassigned'] = []

def save_strategem(name=None, sequence=None):
    global strategems  # Use the global variable
    if name is not None and sequence is not None:
        strategems[name] = sequence
    # Order the strategems dictionary by key in ascending order
    strategems = dict(sorted(strategems.items()))
    # Save the updated strategems dictionary to a JSON file
    with open(strategems_path, 'w') as f:
        json.dump(strategems, f)

# Load macro bindings from a JSON file
try:
    with open(macros_path, 'r') as f:
        macros_json = json.load(f)
        # Order the macros_json dictionary by key in ascending order
        macros_json_ordered = dict(sorted(macros_json.items()))
        # Map string keys to Key objects
        macros = {getattr(Key, k): strategems[v] for k, v in macros_json_ordered.items()}
except KeyError as e:
    print(f"KeyError: {e}")
    # Initialize an empty dictionary if the file does not exist
    macros_json_ordered = {"delete": "Unassigned", "down": "Unassigned", "end": "Unassigned", "home": "Unassigned", "insert": "Unassigned", "left": "Unassigned", "page_down": "Unassigned", "page_up": "Unassigned", "right": "Unassigned", "up": "Unassigned"}
    # Map string keys to Key objects
    macros = {getattr(Key, k): strategems[v] for k, v in macros_json_ordered.items()}
    macros = {}
except FileNotFoundError as e:
    print(f"FileNotFoundError: {e}")
    # Initialize an empty dictionary if the file does not exist
    macros_json_ordered = {"delete": "Unassigned", "down": "Unassigned", "end": "Unassigned", "home": "Unassigned", "insert": "Unassigned", "left": "Unassigned", "page_down": "Unassigned", "page_up": "Unassigned", "right": "Unassigned", "up": "Unassigned"}
    # Map string keys to Key objects
    macros = {getattr(Key, k): strategems[v] for k, v in macros_json_ordered.items()}
    macros = {}  # Initialize an empty dictionary if the file does not exist

def save_macros():
    global macros, strategems  # Use the global variables
    with open(macros_path, 'w') as f:
        # Ensure 'Unassigned' is a key in strategems
        if 'Unassigned' not in strategems:
            strategems['Unassigned'] = []

        # Now create reverse_strategems
        reverse_strategems = {tuple(v): k for k, v in strategems.items()}
        # Create a dictionary from the macros with the keys converted to strings and the values replaced with the names of the strategems
        macros_dict = {k.name: reverse_strategems[tuple(v)] for k, v in macros.items() if tuple(v) in reverse_strategems}
        # Order the macros_dict dictionary by key in ascending order
        macros_dict = dict(sorted(macros_dict.items()))
        json.dump(macros_dict, f)

# Define a function to execute a sequence of key presses and releases
def execute_macro(key_sequence):
    for key in key_sequence:
        keyboard.press(key)     # press the key
        time.sleep(0.05)        # wait for 50 ms
        keyboard.release(key)   # release the key
        time.sleep(0.05)        # wait for 50 ms

# Listen for keypresses in a separate thread
def start_listener(stop_event, on_press):
    listener = Listener(on_press=on_press)
    listener.start()
    while not stop_event.is_set():
        time.sleep(0.1)         # Wait for 100 ms
    listener.stop()

class MacroApp(QWidget):
    def __init__(self, stop_event):
        super().__init__()  # Call the constructor of the parent class QWidget
        self.resize(800, 1024)
        self.stop_event = stop_event  # Store the stop_event parameter in an instance variable

        # Set the window title
        self.setWindowTitle("Hell Divers 2 - Strategem Macro Controller")

        # Create a new QGridLayout and assign it to an instance variable
        self.layout = QGridLayout()

        # Create a new QLabel and assign it to an instance variable
        self.status_label = QLabel()
        self.update_status_label()  # Update the text of the status label

        # Create a new QPushButton, set its text, and connect its clicked signal to the toggle_status method
        self.toggle_status_button = QPushButton("Toggle Status")
        self.toggle_status_button.clicked.connect(self.toggle_status)

        # Create a new QLabel for the key bindings
        self.key_bindings_label = QLabel()
        self.key_bindings_label.setText("Up -> I\nLeft -> J\nDown -> K\nRight -> L")
        self.key_bindings_label.setAlignment(Qt.AlignRight)

        # Add the status label, the key bindings label and the toggle status button to the layout
        self.layout.addWidget(self.status_label, 0, 0, 1, 1)  # Span the status label across 3 columns
        self.layout.addWidget(self.toggle_status_button, 0, 1, 1, 1)  # Move the toggle status button to the next row
        self.layout.addWidget(self.key_bindings_label, 1, 0, 1, 3)  # Span the key bindings label across 3 columns

        # Add the status label and the toggle status button to the layout
        self.layout.addWidget(self.status_label, 0, 0)
        self.layout.addWidget(self.toggle_status_button, 0, 1)

        # Define the keys and macros as instance variables
        self.keys = ['insert', 'home', 'page_up', 'delete', 'end', 'page_down', 'up', 'left', 'down', 'right']
        self.macros = list(strategems.keys())

        # Initialize empty lists for the key labels, macro labels, and key buttons
        self.key_labels = []
        self.macro_labels = []
        self.key_buttons = []

        # Define the positions of the widgets in the grid layout
        positions = [(1, 0), (1, 1), (1, 2), (2, 0), (2, 1), (2, 2), (3, 1), (4, 0), (4, 1), (4, 2)]

        # Loop over the positions and keys
        for position, key in zip(positions, self.keys):
            # Find the macro name that corresponds to the current key
            macro_name = [k for k, v in strategems.items() if v == macros[getattr(Key, key)]][0]

            # Create a new QLabel for the key, set its style, and add it to the list of key labels
            key_label = QLabel(f"{key.capitalize()}")
            key_label.setStyleSheet("border: 2px solid white; padding: 5px; font-weight: bold; background-color: black; color: white;")
            key_label.setAlignment(Qt.AlignCenter)
            self.key_labels.append(key_label)

            # Create a new QLabel for the macro, set its style, and add it to the list of macro labels
            macro_label = QLabel(f"{macro_name}")
            macro_label.setStyleSheet("border: 2px solid black; padding: 5px; font-style: italic; background-color: white; color: red;")
            macro_label.setAlignment(Qt.AlignCenter)
            self.macro_labels.append(macro_label)

            # Create a new QPushButton, set its style, connect its clicked signal to the create_callback method, and add it to the list of key buttons
            button = QPushButton("Change Macro")
            button.setStyleSheet("""
                QPushButton {
                    border: 2px solid black;
                    padding: 5px;
                    background-color: lightblue;
                    color: black;
                    border-radius: 5px;
                    border: 5px outset white;
                }
                QPushButton:hover {
                    background-color: lightgreen;
                }
            """)   
            button.clicked.connect(self.create_callback(key))
            button.pressed.connect(self.button_pressed)
            button.released.connect(self.button_released)
            self.key_buttons.append(button)

            # Create a new QFrame, set its shape and shadow, create a new QVBoxLayout, add the key label, macro label, and button to the layout, and set the layout of the frame
            frame = QFrame()
            frame.setFrameShape(QFrame.StyledPanel)
            frame.setFrameShadow(QFrame.Raised)
            frame.setStyleSheet("""
                background-color: lightgray;
                color: black;
            """)
            frame_layout = QVBoxLayout()
            frame_layout.addWidget(key_label)
            frame_layout.addWidget(macro_label)
            frame_layout.addWidget(button)
            frame.setLayout(frame_layout)

            # Add the frame to the grid layout at the current position
            self.layout.addWidget(frame, position[0]*2 + 1, position[1])

        # Create a new QGroupBox
        self.strategem_group = QGroupBox("Manage Strategems")
        self.strategem_group.setStyleSheet("QGroupBox { border: 1px solid red; }")
        # Set the height of the QGroupBox
        self.strategem_group.setFixedHeight(110)

        # Create a layout for the group
        group_layout = QGridLayout()

        # Create a new QPushButton, set its text, and connect its clicked signal to the add_strategem method
        self.add_strategem_button = QPushButton("Add Strategem")
        self.add_strategem_button.clicked.connect(self.add_strategem)

        # Add the add strategem button to the group layout
        group_layout.addWidget(self.add_strategem_button, 0, 0)

        # Create a new QPushButton, set its text, and connect its clicked signal to the edit_strategem method
        self.edit_strategem_button = QPushButton("Edit Strategem")
        self.edit_strategem_button.clicked.connect(self.edit_strategem)

        # Add the edit strategem button to the group layout
        group_layout.addWidget(self.edit_strategem_button, 0, 1)

        # Create a new QPushButton, set its text, and connect its clicked signal to the delete_strategem method
        self.delete_strategem_button = QPushButton("Delete Strategem")
        self.delete_strategem_button.clicked.connect(self.delete_strategem)

        # Add the delete strategem button to the group layout
        group_layout.addWidget(self.delete_strategem_button, 0, 2)

        # Set the group layout
        self.strategem_group.setLayout(group_layout)

        # Add the group to the main layout
        self.layout.addWidget(self.strategem_group, 10, 0, 1, 3)
        
        # Set the layout of the widget to the grid layout
        self.setLayout(self.layout)
    
    def button_pressed(self):
        sender = self.sender()
        sender.setStyleSheet("""
            border: 2px solid black;
            padding: 5px;
            background-color: green;
            color: white;
            border-radius: 5px;
            border: 5px outset white;
        """)

    def button_released(self):
        sender = self.sender()
        sender.setStyleSheet("""
            QPushButton {
                border: 2px solid black;
                padding: 5px;
                background-color: lightblue;
                color: black;
                border-radius: 5px;
                border: 5px outset white;
            }
            QPushButton:hover {
                background-color: lightgreen;
            }
        """)

    def create_callback(self, key):
        # This function creates a callback function for a given key.
        # The callback function will call the change_macro method with the given key when invoked.
        return lambda: self.change_macro(key)

    def change_macro(self, key):
        # This function changes the macro associated with a given key.
        # It opens a dialog to let the user select a new macro from the list of available macros.
        selected_macro, ok = QInputDialog.getItem(self, "Select a macro", f"Macros: {key.capitalize()}", self.macros, 0, False)
        # If the user clicked OK and selected a macro, update the macro for the given key.
        if ok and selected_macro:
            macros[getattr(Key, key)] = strategems[selected_macro]
            # Find the name of the selected macro.
            macro_name = [k for k, v in strategems.items() if v == macros[getattr(Key, key)]][0]
            # Update the text of the label for the given key to show the name of the selected macro.
            self.macro_labels[self.keys.index(key)].setText(f"{macro_name}")
            # Save the updated macros dictionary to a JSON file using the save_macros function
            save_macros()
    
    def add_strategem(self):
        # This function adds a new strategem.
        # It opens two dialogs to let the user input the name and the keys of the new strategem.
        strategem_name, ok1 = QInputDialog.getText(self, "Add a strategem", "Name:")
        if ok1:
            lower_case_strategem_name = strategem_name.lower()
            if any(existing_name.lower() == lower_case_strategem_name for existing_name in strategems):
                QMessageBox.warning(self, "Warning", "Strategem already exists!")
            else:
                strategem_keys, ok2 = QInputDialog.getText(self, "Add a strategem", "Keys:")
                # If the user clicked OK and inputted the name and the keys, add the new strategem.
                if ok2 and strategem_name and strategem_keys:
                    strategems[strategem_name] = list(strategem_keys)
                    self.macros.append(strategem_name)
                    save_strategem(strategem_name, strategems[strategem_name])

    def edit_strategem(self):
        # This function edits an existing strategem.
        # It opens two dialogs to let the user select the strategem to edit and input the new keys.
        selected_strategem, ok1 = QInputDialog.getItem(self, "Edit a strategem", "Strategem:", self.macros, 0, False)
        if ok1:            
            new_keys, ok2 = QInputDialog.getText(self, "Edit a strategem", "New keys:")
            # If the user clicked OK and selected a strategem and inputted the new keys, update the strategem.
            if ok2 and selected_strategem and new_keys:
                strategems[selected_strategem] = list(new_keys)
                save_strategem(selected_strategem, strategems[selected_strategem])
            
    def delete_strategem(self):
        # This function deletes an existing strategem.
        # It opens a dialog to let the user select the strategem to delete.
        selected_strategem, ok = QInputDialog.getItem(self, "Delete a strategem", "Strategem:", self.macros, 0, False)
        # If the user clicked OK and selected a strategem, delete the strategem.
        if ok and selected_strategem:
            # If the strategem is currently bound to a macro, then set that macro to Unassigned.
            for key, macro in macros.items():
                if macro == strategems[selected_strategem]:
                    macros[key] = 'Unassigned'
                    # Update the text of the label for the given key to show 'Unassigned'.
                    self.macro_labels[self.keys.index(key.name)].setText('Unassigned')
            # Remove the strategem from the strategems dictionary and the macros list.
            del strategems[selected_strategem]
            self.macros.remove(selected_strategem)
            # Save the updated strategems dictionary and macros list to a JSON file using the save_strategems and save_macros functions
            save_strategem()
            save_macros()

    def on_press(self, key):  # Define a function to handle keypress events
        global running  # Access the global running variable
        if key == Key.f12:        
            running = not running  # Toggle the boolean value of running variable
            self.update_status_label()  # Update the status label
        if key in macros and running:  # If the key is in macros and running is True
            self.toggle_status()  # Toggle the running status
            with keyboard.pressed(Key.ctrl_l):
                time.sleep(0.2)  # Wait for 100 ms
                # Get the strategem name from the strategems dictionary
                strategem_name = [name for name, sequence in strategems.items() if sequence == macros[key]][0]
                # Print the key and the associated strategem
                strategem_name = strategem_name.ljust(25)
                print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {strategem_name}")
                execute_macro(macros[key])  # Execute the macro associated with the key            
                time.sleep(0.3)  # Wait for 100 ms
            self.toggle_status()  # Toggle the running status

    def toggle_status(self):
        # This function toggles the running status of the application.
        # It updates the global running variable and the text and color of the status label.
        global running
        running = not running
        self.update_status_label()

    def update_status_label(self):
        # This function updates the text and color of the status label based on the running status of the application.
        global running
        if running:
            # If the application is running, set the text to "Status: Running" and the color to green.
            self.status_label.setText("Status: Running")
            self.status_label.setStyleSheet("color: green;")
        else:
            # If the application is not running, set the text to "Status: Stopped" and the color to red.
            self.status_label.setText("Status: Stopped")
            self.status_label.setStyleSheet("color: red;")
    
    def closeEvent(self, event):
        self.stop_event.set()  # Signal the listener thread to stop
        event.accept()  # Let the window close

stop_event = threading.Event()
app = QApplication([])
window = MacroApp(stop_event)
listener_thread = threading.Thread(target=start_listener, args=(stop_event, window.on_press))
listener_thread.start()

window.show()
app.exec_()