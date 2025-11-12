#!/usr/bin/env python3
"""
Simple test to verify pynput keyboard listener is working.
Press any key - it should print to console. Press ESC to exit.
"""
from pynput.keyboard import Listener, Key
import sys

def on_press(key):
    try:
        print(f"Key pressed: {key.char}")
    except AttributeError:
        print(f"Special key pressed: {key}")

    # Exit on ESC
    if key == Key.esc:
        print("ESC pressed - exiting")
        return False

def on_release(key):
    pass

print("Testing pynput keyboard listener...")
print(f"Platform: {sys.platform}")
print("Press any key (ESC to exit)...")
print("-" * 40)

try:
    with Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()
except Exception as e:
    print(f"ERROR: {e}")
    print("\nThis might be a permissions issue on Linux.")
    print("pynput requires X11 access to capture keyboard events.")
    print("\nTry running with:")
    print("  export DISPLAY=:0")
    print("  python test_pynput.py")
