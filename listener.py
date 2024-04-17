import json, time
from pynput.keyboard import Listener, Key, Controller
import datetime

# Create a keyboard controller
keyboard = Controller()

# KeyboardListener class
class KeyboardListener:
    # Constructor
    def __init__(self, stratagems_file, macro_file):
        self.stratagems_file = stratagems_file
        self.macro_file = macro_file
        self.stratagems = {}    # Dictionary to store Stratagems
        self.bindings = {}      # Dictionary to store macro bindings
        self.load_stratagems()  # Load Stratagems from a JSON file
        self.load_macros()      # Load macro bindings from a JSON file
        self.running = True     # Control the running of the listener loop

    # Load Stratagems from a JSON file
    def load_stratagems(self):
        """Load Stratagems from a JSON file."""
        try:
            with open(self.stratagems_file, 'r') as file:
                self.stratagems = json.load(file)
        except FileNotFoundError:
            print("Stratagems file not found.")
        except json.JSONDecodeError:
            print("Error decoding the Stratagems file.")

    # Load macro bindings from a JSON file
    def load_macros(self):
        """Load macro bindings from a JSON file."""
        try:
            with open(self.macro_file, 'r') as file:
                self.bindings = json.load(file)
        except FileNotFoundError:
            print("Macro file not found.")
        except json.JSONDecodeError:
            print("Error decoding the macro file.")

    # Callback function for key press event
    def on_press(self, key):
        try:
            key_name = key.char if hasattr(key, 'char') else key.name           # Get the key name
            if key_name in self.bindings:                                       # Check if the key name is in the bindings
                stratagem_name = self.bindings[key_name]
                stratagem_sequence = self.stratagems.get(stratagem_name, [])
                self.execute_stratagem(stratagem_name, stratagem_sequence)      # Execute the stratagem
        except AttributeError:
            pass

    # Execute a stratagem
    def execute_stratagem(self, name, sequence):
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"{current_time} - {name} - {sequence}")
        # Call down stratagem
        with keyboard.pressed(Key.ctrl_l):  # Press and hold the left control key
            time.sleep(0.1)
            for key in sequence:
                keyboard.press(key)         # press the key
                time.sleep(0.05)            # wait for 50 ms
                keyboard.release(key)       # release the key
                time.sleep(0.05)            # wait for 50 ms

    # Start the listener loop
    def start(self):
        while self.running:
            with Listener(on_press=self.on_press) as listener:
                listener.join()

    # Stop the listener loop
    def stop(self):
        self.running = False  # Set running to False to stop the loop