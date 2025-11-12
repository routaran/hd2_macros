"""
Helldivers 2 Stratagem Macro Manager - Keyboard Listener Module

This module handles keyboard input monitoring and stratagem macro execution.
It listens for configured macro keys and executes the corresponding stratagem
sequences in the game.
"""

import json
import time
from pynput.keyboard import Listener, Key, Controller
import datetime
import logging
import threading
from typing import Dict, List

# Setup logging
logger = logging.getLogger(__name__)

# Create a keyboard controller
keyboard = Controller()

# Constants for timing
STRATAGEM_ACTIVATION_DELAY = 0.1  # Delay after pressing Control key (100ms)
KEY_PRESS_DURATION = 0.05          # How long to hold each directional key (50ms)
KEY_RELEASE_DELAY = 0.05           # Delay between key presses (50ms)

class KeyboardListener:
    """
    Keyboard listener for Helldivers 2 stratagem macros.

    This class monitors keyboard input for configured macro keys and executes
    the corresponding stratagem sequences by simulating key presses.

    Attributes:
        stratagems_file: Path to the stratagems JSON configuration file
        macro_file: Path to the macros JSON configuration file
        stratagems: Dictionary mapping stratagem names to key sequences
        bindings: Dictionary mapping macro keys to stratagem names
        running: Flag to control the listener loop
        data_lock: Threading lock for thread-safe data access
    """
    def __init__(self, stratagems_file: str, macro_file: str) -> None:
        """
        Initialize the KeyboardListener.

        Args:
            stratagems_file: Path to the stratagems JSON configuration file
            macro_file: Path to the macros JSON configuration file
        """
        self.stratagems_file = stratagems_file
        self.macro_file = macro_file
        self.stratagems: Dict[str, List[str]] = {}  # Dictionary to store Stratagems
        self.bindings: Dict[str, str] = {}           # Dictionary to store macro bindings
        self.data_lock = threading.Lock()            # Lock for thread-safe data access
        self.running = True                          # Control the running of the listener loop
        self.listener_instance = None                # Store listener instance

        self.load_stratagems()  # Load Stratagems from a JSON file
        self.load_macros()      # Load macro bindings from a JSON file

        logger.info("KeyboardListener initialized")

    def load_stratagems(self) -> None:
        """
        Load stratagems from a JSON file.

        If the file doesn't exist or is malformed, generates default stratagems.
        Uses thread-safe locking during data modification.
        """
        try:
            with open(self.stratagems_file, 'r') as file:
                loaded_stratagems = json.load(file)

            with self.data_lock:
                self.stratagems = loaded_stratagems

            logger.info(f"Loaded {len(self.stratagems)} stratagems from {self.stratagems_file}")
        except FileNotFoundError:
            logger.warning(f"Stratagems file not found: {self.stratagems_file}")
            self.generate_empty_stratagems()
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding stratagems file: {e}")
            self.generate_empty_stratagems()
        except Exception as e:
            logger.error(f"Unexpected error loading stratagems: {e}")
            self.generate_empty_stratagems()

    def load_macros(self) -> None:
        """
        Load macro bindings from a JSON file.

        If the file doesn't exist or is malformed, generates default macros.
        Uses thread-safe locking during data modification.
        """
        try:
            with open(self.macro_file, 'r') as file:
                loaded_bindings = json.load(file)

            with self.data_lock:
                self.bindings = loaded_bindings

            logger.info(f"Loaded {len(self.bindings)} macro bindings from {self.macro_file}")
        except FileNotFoundError:
            logger.warning(f"Macro file not found: {self.macro_file}")
            self.generate_empty_macros()
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding macro file: {e}")
            self.generate_empty_macros()
        except Exception as e:
            logger.error(f"Unexpected error loading macros: {e}")
            self.generate_empty_macros()

    def generate_empty_macros(self) -> None:
        """
        Generate default macro bindings.

        Creates a default set of 10 macro keys with some assigned to common stratagems.
        Uses thread-safe locking during data modification.
        """
        default_bindings = {
            "insert": "Mission - Reinforce",
            "home": "Mission - Resupply",
            "page_up": "Unassigned",
            "delete": "Unassigned",
            "end": "Unassigned",
            "page_down": "Unassigned",
            "up": "Unassigned",
            "left": "Unassigned",
            "down": "Unassigned",
            "right": "Unassigned"
        }

        with self.data_lock:
            self.bindings = default_bindings

        logger.info("Generated default macro bindings")

    def generate_empty_stratagems(self) -> None:
        """
        Generate default stratagems.

        Creates a default set of basic mission stratagems.
        Uses thread-safe locking during data modification.
        """
        default_stratagems = {
            "Mission - Reinforce": ["i", "k", "l", "j", "i"],
            "Mission - Resupply": ["k", "k", "i", "l"],
            "Mission - SEAF Artillery": ["l", "i", "i", "k"],
            "Mission - Hellbomb": ["k", "i", "j", "k", "i", "l", "k", "i"],
            "Eagle - Recovery": ["i", "i", "j", "i", "l"]
        }

        with self.data_lock:
            self.stratagems = default_stratagems

        logger.info("Generated default stratagems")

    def on_press(self, key) -> None:
        """
        Callback function triggered on key press.

        Checks if the pressed key matches a configured macro binding and
        executes the corresponding stratagem if found. Uses thread-safe
        data access.

        Args:
            key: The key that was pressed
        """
        try:
            key_name = key.char if hasattr(key, 'char') else key.name  # Get the key name
            logger.debug(f"Key pressed: {key_name} (type: {type(key).__name__})")

            # Thread-safe check of bindings
            with self.data_lock:
                logger.debug(f"Current bindings: {list(self.bindings.keys())}")
                if key_name in self.bindings:
                    stratagem_name = self.bindings[key_name]
                    stratagem_sequence = self.stratagems.get(stratagem_name, [])

            # Execute stratagem if valid
            if key_name in self.bindings and stratagem_sequence:
                logger.debug(f"Macro triggered for key: {key_name}")
                self.execute_stratagem(stratagem_name, stratagem_sequence)
            else:
                if key_name in self.bindings:
                    logger.warning(f"No stratagem sequence found for: {self.bindings[key_name]}")
        except AttributeError:
            # Ignore keys without char or name attributes
            pass
        except Exception as e:
            logger.error(f"Error in on_press: {e}")

    def execute_stratagem(self, name: str, sequence: List[str]) -> None:
        """
        Execute a stratagem by simulating key presses.

        Holds down the Left Control key and sequences through the directional
        keys with precise timing to trigger the stratagem in-game.

        Args:
            name: Name of the stratagem being executed
            sequence: List of keys to press in order (i, j, k, l)
        """
        if not sequence:
            logger.warning(f"Attempted to execute empty stratagem: {name}")
            return

        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        logger.info(f"{current_time} - Executing: {name} - {sequence}")

        try:
            # Call down stratagem
            with keyboard.pressed(Key.ctrl_l):  # Press and hold the left control key
                time.sleep(STRATAGEM_ACTIVATION_DELAY)
                for key in sequence:
                    keyboard.press(key)                  # Press the directional key
                    time.sleep(KEY_PRESS_DURATION)      # Hold for configured duration
                    keyboard.release(key)                # Release the key
                    time.sleep(KEY_RELEASE_DELAY)       # Wait before next key
        except Exception as e:
            logger.error(f"Error executing stratagem '{name}': {e}")

    def start(self) -> None:
        """
        Start the keyboard listener.

        Creates a single listener instance that runs until stopped.
        This fixes the inefficiency of recreating the listener in a loop.
        """
        logger.info("Starting keyboard listener")
        try:
            with Listener(on_press=self.on_press) as listener:
                logger.info("Keyboard listener is now active and listening for key presses")
                self.listener_instance = listener
                while self.running:
                    time.sleep(0.1)  # Prevent busy waiting
                listener.stop()
        except Exception as e:
            logger.error(f"Error in listener: {e}")
        finally:
            logger.info("Keyboard listener stopped")

    def stop(self) -> None:
        """
        Stop the keyboard listener.

        Sets the running flag to False, which causes the listener loop to exit.
        """
        logger.info("Stopping keyboard listener")
        self.running = False