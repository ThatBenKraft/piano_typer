"""
### Main
Runs full piano typer, converting piano keystrokes into computer inputs, mouse
movements, and display visuals.
"""

import json
import os
import sys
from pathlib import Path

import keyboard
import mouse

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"
from pygame.time import Clock

import midi
from packaging import Keystroke
from visuals import Display

__author__ = "Ben Kraft"
__copyright__ = "None"
__credits__ = "Ben Kraft"
__license__ = "Apache"
__version__ = "0.3.0"
__maintainer__ = "Ben Kraft"
__email__ = "ben.kraft@rcn.com"
__status__ = "Prototype"


class Paths:
    KEYBINDS = Path(__file__).parent / "keybinds.json"


class Defaults:
    PIANO_MODE = False
    KEY_LOG = True
    SCALE = 0.5
    FRAMERATE = 60
    SENSITIVITY = 100


class Keybinds:
    try:
        _json = json.load(open(Paths.KEYBINDS, "r"))
    except FileNotFoundError:
        print(f"Keybinds file not found at {Paths.KEYBINDS}")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error decoding keybinds file at {Paths.KEYBINDS}")
        sys.exit(1)

    KEYBOARD: dict[str, str] = _json["keyboard"]
    MOUSE: dict[str, str] = _json["mouse"]
    CURSOR: dict[str, list[int]] = _json["cursor"]
    QUIT: str = _json["quit"]
    SLOW: str = _json["slow"]


class Program:
    """
    A class to run piano typer

    Attributes:
        piano_mode: If keystokes will be displayed but not acted upon.
        key_log: If keystrokes will be logged.
        sensitivity: How quickly the cursor moves when a key is held.
    """

    def __init__(
        self,
        piano_mode=Defaults.PIANO_MODE,
        key_log=Defaults.KEY_LOG,
        scale=Defaults.SCALE,
        sensitivity=Defaults.SENSITIVITY,
        framerate=Defaults.FRAMERATE,
    ) -> None:
        """
        Initializes a Program object with piano mode, key log, and sensitivity.

        Args:
            piano_mode: If keystokes will be displayed but not acted upon.
            key_log: If keystrokes will be logged.
            sensitivity: How quickly the cursor moves when a key is held.
        """
        self.PIANO_MODE = piano_mode
        self.KEY_LOG = key_log
        self.sensitivity = sensitivity
        self.framerate = framerate
        self.clock = Clock()
        self._midi_device = midi.get_device()
        self._display = Display(scale=scale)
        self.held_keystrokes: set[Keystroke] = set()

    def update_held_keystrokes(self, keystroke: Keystroke) -> None:
        """
        Updates list of held keystrokes with new keystroke.
        """
        # Adds or removes from held keys
        if keystroke.is_press:
            self.held_keystrokes.add(keystroke)
        elif not keystroke.is_press and keystroke in self.held_keystrokes:
            self.held_keystrokes.remove(keystroke)

    def process_button(self, keystroke: Keystroke) -> None:
        """
        Toggles device if keystroke is in appropirate keybinds.
        """
        # Presses corresponding keyboard button
        if keystroke in Keybinds.KEYBOARD:
            hotkey = Keybinds.KEYBOARD[str(keystroke)]
            keyboard.press(hotkey) if keystroke.is_press else keyboard.release(hotkey)
        # Presses corresponding mouse button
        elif keystroke in Keybinds.MOUSE:
            hotkey = Keybinds.MOUSE[str(keystroke)]
            mouse.press(hotkey) if keystroke.is_press else mouse.release(hotkey)

    def process_cursor(self) -> None:
        """
        Moves mouse based on held directions.
        """
        # Returns early if no held keys
        if not self.held_keystrokes:
            return
        # Gets held directions as integer lists from display
        held_directions = [
            Keybinds.CURSOR[str(keystroke)]
            for keystroke in self.held_keystrokes
            if keystroke in Keybinds.CURSOR
        ]
        # Returns early if no held directions
        if not held_directions:
            return
        # Creates a list of two tuples for each direction
        axes = zip(*held_directions)
        # Determines mouse movement speed from sensitivity, framerate, and if the slow key is pressed
        speed = 1 if Keybinds.SLOW in self.held_keystrokes else 5
        move_factor = round(self.sensitivity / self.framerate * speed)
        # Sums and scales directions
        move_x, move_y = (sum(axis) * move_factor for axis in axes)
        # Moves mouse in direction
        mouse.move(move_x, move_y, absolute=False, duration=0)

    def _logic_tick(self) -> bool:
        """
        Runs program logic loop. Returns false if loop should stop.
        """
        # Handles display closing
        if self._display.is_closed():
            print("\nExiting via display...")
            return False
        # Gets keystroke
        keystrokes = midi.get_keystrokes(self._midi_device)
        # Processes keystrokes if populated
        for keystroke in keystrokes:
            if keystroke == Keybinds.QUIT and not self.PIANO_MODE:
                print(f"\nExiting via {Keybinds.QUIT} key...")
                return False
            # If key log is active, prints keystroke
            if self.KEY_LOG:
                print(keystroke.details())
            # Manages held list
            self.update_held_keystrokes(keystroke)
            # Processes button presses/releases
            if not self.PIANO_MODE:
                self.process_button(keystroke)
        # Processes held cursor movements
        if not self.PIANO_MODE:
            self.process_cursor()
        # Updates display with currently held keys
        self._display.refresh(self.held_keystrokes)
        return True

    def tick(self, framerate=Defaults.FRAMERATE):
        """
        Waits to match specified framerate.
        """
        self.clock.tick(framerate)

    def run(self):
        """
        Runs main program loop until display is closed or Ctrl+C is pressed.
        Updates display with keystrokes and moves cursor based on held directions.
        """
        try:
            run = True
            # Runs logic loop unless stopped
            while run:
                run = self._logic_tick()
                self.tick(self.framerate)
        except KeyboardInterrupt:
            print("\nExiting via interrupt...")
        finally:
            self.close()

    def close(self):
        self._midi_device.close()
        self._display.close()


def main() -> None:
    """
    Runs main controller actions.
    """
    piano_mode = Defaults.PIANO_MODE
    key_log = Defaults.KEY_LOG
    # Argument handling
    if "--help" in sys.argv:
        print("\nUse -p for piano mode (no controls) or -nl to turn off keylog.\n")
        return
    # Enters piano mode
    if "-p" in sys.argv:
        print("\nStarting in PIANO MODE. . .")
        piano_mode = True
    # Disables key log
    if "-nl" in sys.argv:
        print("\nDisabling KEY LOG. . .")
        key_log = False

    # Runs program
    program = Program(piano_mode, key_log)
    program.run()
    # Ends program
    print("\nThanks for using the keyboard swap!\n")


if __name__ == "__main__":
    main()
