import json, time
from pynput.keyboard import Listener, Key, Controller

keyboard = Controller()

class KeyboardListener:
    def __init__(self, strategems_file, macro_file):
        self.strategems_file = strategems_file
        self.macro_file = macro_file
        self.strategems = {}
        self.bindings = {}
        self.load_strategems()
        self.load_macros()
        self.running = True  # Control the running of the listener loop

    def load_strategems(self):
        """Load strategems from a JSON file."""
        try:
            with open(self.strategems_file, 'r') as file:
                self.strategems = json.load(file)
        except FileNotFoundError:
            print("Strategems file not found.")
        except json.JSONDecodeError:
            print("Error decoding the strategems file.")

    def load_macros(self):
        """Load macro bindings from a JSON file."""
        try:
            with open(self.macro_file, 'r') as file:
                self.bindings = json.load(file)
        except FileNotFoundError:
            print("Macro file not found.")
        except json.JSONDecodeError:
            print("Error decoding the macro file.")

    def on_press(self, key):
        try:
            key_name = key.char if hasattr(key, 'char') else key.name
            if key_name in self.bindings:
                strategem_name = self.bindings[key_name]
                strategem_sequence = self.strategems.get(strategem_name, [])
                self.execute_strategem(strategem_name, strategem_sequence)
        except AttributeError:
            pass

    def execute_strategem(self, name, sequence):
        # Example of what could be done with the sequence; custom handling needed
        print(f"Executing {name}: {sequence}")
        # You might simulate key presses or other actions based on sequence
        """  with keyboard.pressed(Key.ctrl_l):
            time.sleep(0.1)
            for key in sequence:
                keyboard.press(key)     # press the key
                time.sleep(0.05)        # wait for 50 ms
                keyboard.release(key)   # release the key
                time.sleep(0.05)        # wait for 50 ms """

    def start(self):
        while self.running:
            with Listener(on_press=self.on_press) as listener:
                listener.join()

    def stop(self):
        self.running = False  # Set running to False to stop the loop

# Example usage
if __name__ == "__main__":
    listener = KeyboardListener('strategems.json', 'macros.json')
    listener.start()
