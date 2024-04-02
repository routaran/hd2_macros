from pynput.keyboard import Key, Controller, Listener
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QInputDialog, QGridLayout, QFrame
import time, threading

# Create keyboard controller object
keyboard = Controller()

# Variable to track of the state of the macro listener
running = True

# list of strategem codes # https://steamcommunity.com/sharedfiles/filedetails/?id=3160501535
strategems = {
    'Mission - Reinforce': ['i', 'k', 'l', 'j', 'i'],
    'Mission - Resupply': ['k', 'k', 'i', 'l'],
    'Mission - SEAF Artillery': ['l','i','i','k'],
    'Weapon - Grenade Launcher': ['k', 'j', 'i', 'j', 'k'],
    'Weapon - Antitank': ['k', 'k', 'j', 'i', 'r'],
    'Weapon - Recoiless_rifle': ['k','j','l','l','j'],
    'Weapon - ArcThrower': ['k', 'l', 'k', 'i', 'j', 'j'],
    'Weapon - Autocannon': ['k', 'l', 'k', 'i', 'j', 'j'],
    'Weapon - Railgun': ['k', 'l', 'k', 'i', 'j', 'l'],
    'Orbital - PrecisionStrike': ['l', 'l', 'i'],
    'Orbital - 380mm': ['l', 'k', 'i', 'i', 'j', 'k', 'k'],
    'Orbital - Laser': ['l', 'k', 'i', 'l', 'k'],
    'Orbital - Railcannon': ['l', 'i','k','k','l'],
    'Eagle - Airstrike': ['i', 'l', 'k', 'l'],
    'Eagle - Cluster': ['i', 'l', 'k', 'k', 'l'],
    'Eagle - 500 KG': ['i', 'l', 'k', 'k', 'k'],
    'Backpack - Jump Pack': ['k', 'i', 'i', 'k', 'i'],
    'Backpack - Guarddog': ['k', 'i', 'j', 'i', 'l', 'l'],
    'Backpack - Suppply': ['k', 'j', 'k', 'i', 'k'],
    'Backpack - Shield Gen': ['k', 'i', 'j', 'l', 'j', 'l'],
    'Sentry - Gattling': ['k', 'i', 'l', 'j'],
    'Sentry - Mortar': ['k', 'i', 'l', 'l', 'k'],
    'Sentry - Autocannon': ['k', 'i', 'l', 'i', 'j', 'i'],
    'Sentry - Rocket': ['k', 'i', 'l', 'l', 'j']
}

# Define macros
macros = {
    Key.insert: strategems['Mission - Reinforce'],          # mission
    Key.home: strategems['Mission - Resupply'],             # mission
    Key.page_up: strategems['Weapon - Grenade Launcher'],   # support
    Key.page_down: strategems['Backpack - Guarddog'],       # engineering
    Key.delete: strategems['Eagle - Cluster'],              # hangar/orbital (big)
    Key.end: strategems['Eagle - Airstrike'],               # hangar/orbital (small)
    Key.left: strategems['Sentry - Gattling'],              # sentry
    Key.up: strategems['Sentry - Autocannon'],              # sentry (anti armor)
    Key.down: strategems['Weapon - Antitank'],              # misc
    Key.right: strategems['Weapon - Recoiless_rifle'],      # misc
}


# Define a function to execute a sequence of key presses and releases
def execute_macro(key_sequence):
    for key in key_sequence:
        keyboard.press(key)     # press the key
        time.sleep(0.05)        # wait for 50 ms
        keyboard.release(key)   # release the key
        time.sleep(0.05)        # wait for 50 ms


def on_press(key):                          # Define a function to handle keypress events
    global running                          # Access the global running variable
    if key == Key.f12:        
        running = not running               # Toggle the boolean value of running variable
    if key in macros and running:           # If the key is in macros and running is True
        with keyboard.pressed(Key.ctrl_l):
            time.sleep(0.1)                 # Wait for 100 ms
            # Get the strategem name from the strategems dictionary
            strategem_name = [name for name, sequence in strategems.items() if sequence == macros[key]][0]
            # Print the key and the associated strategem
            print(f"Executing strategem: {key} - {strategem_name}")  
            execute_macro(macros[key])      # Execute the macro associated with the key            
            time.sleep(0.1)                 # Wait for 100 ms

class MacroApp(QWidget):
    def __init__(self, stop_event):
        super().__init__()
        self.stop_event = stop_event

        self.setWindowTitle("Hell Divers 2 - Strategem Macro Controller")

        self.layout = QGridLayout()

        self.status_label = QLabel()
        self.update_status_label()

        self.toggle_status_button = QPushButton("Toggle Status")
        self.toggle_status_button.clicked.connect(self.toggle_status)

        self.layout.addWidget(self.status_label, 0, 0)
        self.layout.addWidget(self.toggle_status_button, 0, 1)

        self.keys = ['insert', 'home', 'page_up', 'delete', 'end', 'page_down', 'up', 'left', 'down', 'right']
        self.macros = list(strategems.keys())

        self.key_labels = []
        self.macro_labels = []
        self.key_buttons = []

        positions = [(0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (1, 2), (2, 1), (3, 0), (3, 1), (3, 2)]

        for position, key in zip(positions, self.keys):
            macro_name = [k for k, v in strategems.items() if v == macros[getattr(Key, key)]][0]
            
            key_label = QLabel(f"{key.capitalize()}")
            key_label.setStyleSheet("border: 1px solid black; padding: 5px; font-weight: bold; background-color: lightgray; color: black;")
            self.key_labels.append(key_label)

            macro_label = QLabel(f"{macro_name}")
            macro_label.setStyleSheet("border: 1px solid black; padding: 5px; font-style: italic; background-color: white; color: black;")
            self.macro_labels.append(macro_label)

            button = QPushButton("Change Macro")
            button.setStyleSheet("border: 1px solid black; padding: 5px; background-color: lightblue; color: black;")
            button.clicked.connect(self.create_callback(key))
            self.key_buttons.append(button)

            # Create a frame to hold the label and button
            frame = QFrame()
            frame.setFrameShape(QFrame.StyledPanel)
            frame.setFrameShadow(QFrame.Raised)
            frame_layout = QVBoxLayout()
            frame_layout.addWidget(key_label)
            frame_layout.addWidget(macro_label)
            frame_layout.addWidget(button)
            frame.setLayout(frame_layout)

            self.layout.addWidget(frame, position[0]*2 + 1, position[1])

        self.setLayout(self.layout)

    def create_callback(self, key):
        return lambda: self.change_macro(key)

    def change_macro(self, key):
        selected_macro, ok = QInputDialog.getItem(self, "Select a macro", "Macros:", self.macros, 0, False)
        if ok and selected_macro:
            macros[getattr(Key, key)] = strategems[selected_macro]
            macro_name = [k for k, v in strategems.items() if v == macros[getattr(Key, key)]][0]
            self.macro_labels[self.keys.index(key)].setText(f"{macro_name}")

    def toggle_status(self):
        global running
        running = not running
        self.update_status_label()

    def update_status_label(self):
        global running
        if running:
            self.status_label.setText("Status: Running")
            self.status_label.setStyleSheet("color: green;")
        else:
            self.status_label.setText("Status: Stopped")
            self.status_label.setStyleSheet("color: red;")
    
    def closeEvent(self, event):
        self.stop_event.set()  # Signal the listener thread to stop
        event.accept()  # Let the window close

# Listen for keypresses in a separate thread
def start_listener(stop_event):
    listener = Listener(on_press=on_press)
    listener.start()
    while not stop_event.is_set():
        time.sleep(0.1)  # Wait for 100 ms
    listener.stop()

stop_event = threading.Event()
listener_thread = threading.Thread(target=start_listener, args=(stop_event,))
listener_thread.start()

app = QApplication([])
window = MacroApp(stop_event)
window.show()
app.exec_()
