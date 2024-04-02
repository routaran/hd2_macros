from pynput.keyboard import Key, Controller, Listener
import time

# Create keyboard controller object
keyboard = Controller()

# list of strategem codes # https://steamcommunity.com/sharedfiles/filedetails/?id=3160501535
reinforce = ['i', 'k', 'l', 'j', 'i']
resupply = ['k', 'k', 'i', 'l']
eagleAir = ['i', 'l', 'k', 'l']
precisionStrike = ['l', 'l', 'i']
grenadeLauncher = ['k', 'j', 'i', 'j', 'k']
guardDog = ['k', 'i', 'j', 'i', 'l', 'l']
gattlingSentry = ['k', 'i', 'l', 'j']
Orbital380 = ['l', 'k', 'i', 'i', 'j', 'k', 'k']
eagleCluster = ['i', 'l', 'k', 'k', 'l']
autoSentry = ['k', 'i', 'l', 'i', 'j', 'i']
antitank = ['k', 'k', 'j', 'i', 'r']
supplyBackpack = ['k', 'j', 'k', 'i', 'k']
recoiless_rifle = ['k','j','l','l','j']

# Define macros
macros = {
    Key.insert: reinforce,
    Key.home: resupply,
    Key.page_up: grenadeLauncher,
    Key.delete: eagleCluster,
    Key.end: eagleAir,
    Key.page_down: guardDog,
    Key.left: gattlingSentry,
    Key.up: autoSentry,
    Key.down: antitank,
    Key.right: recoiless_rifle,
}


# Define a function to execute a sequence of key presses and releases
def execute_macro(key_sequence):
    for key in key_sequence:
        keyboard.press(key)     # press the key
        time.sleep(0.05)        # wait for 50 ms
        keyboard.release(key)   # release the key
        time.sleep(0.05)        # wait for 50 ms


def on_press(key):                  # Define a function to handle keypress events
    if key == Key.f12:
        return False  # exit the program
    if key in macros:
        with keyboard.pressed(Key.ctrl_l):
            time.sleep(0.1)  # wait for 100 ms
            # Execute the macro associated with the key
            execute_macro(macros[key])
            # sleep to ensure it finishes
            time.sleep(0.1)  # wait for 100 ms


print("Running Listener")
# Listen for keypresses
with Listener(on_press=on_press) as listener:
    listener.join()  # Start the listener loop
print("Program Complete")
