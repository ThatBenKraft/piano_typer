"""
## Main
Runs full piano typer, converting piano keystrokes into computer inputs, mouse 
movements, and display visuals.
"""

import json
import sys
from pathlib import Path

import keyboard
import mouse

import midi
from packaging import NOTES, Keystroke
from visuals import Display

__author__ = "Ben Kraft"
__copyright__ = "None"
__credits__ = "Ben Kraft"
__license__ = "Apache"
__version__ = "0.2.0"
__maintainer__ = "Ben Kraft"
__email__ = "ben.kraft@rcn.com"
__status__ = "Prototype"


class Paths:
    KEYBINDS = Path(__file__).parent / "keybinds.json"


class Keybinds:
    _json = json.load(open(Paths.KEYBINDS, "r"))
    KEYBOARD: dict[str, str] = _json["keyboard"]
    MOUSE: dict[str, str] = _json["mouse"]
    CURSOR: dict[str, list[int]] = _json["cursor"]
    QUIT: str = _json["quit"]


class Defaults:
    PIANO_MODE = True
    KEY_LOG = True
    SENSITIVITY = 12


class Program:

    def __init__(
        self,
        piano_mode=Defaults.PIANO_MODE,
        key_log=Defaults.KEY_LOG,
        sensitivity=Defaults.SENSITIVITY,
    ) -> None:
        self.PIANO_MODE = piano_mode
        self.KEY_LOG = key_log
        self.SENSITIVITY = sensitivity
        self.midi_device = midi.get_device()
        self.display = Display()

    def process_keystroke(self, keystroke: Keystroke) -> None:
        """
        Toggles device if keystroke is in appropirate keybinds.
        """
        # If key log is active, prints keystroke
        if self.KEY_LOG:
            print(repr(keystroke))
        # Returns early if piano mode
        if self.PIANO_MODE:
            return
        # If in list, presses corresponding keyboard button
        if keystroke.full_note in Keybinds.KEYBOARD:
            hotkey = Keybinds.KEYBOARD[keystroke.full_note]
            keyboard.press(hotkey) if keystroke.press else keyboard.release(hotkey)
        # If in list, presses corresponding mouse button
        elif keystroke.full_note in Keybinds.MOUSE:
            hotkey = Keybinds.MOUSE[keystroke.full_note]
            mouse.press(hotkey) if keystroke.press else mouse.release(hotkey)

    def process_cursor(self) -> None:
        """
        Moves mouse based on held directions.
        """
        # Returns early if no held keys
        if not self.display.held_keystrokes:
            return
        # Gets held directions as integer lists from display
        held_directions = [
            Keybinds.CURSOR[keystroke.full_note]
            for keystroke in self.display.held_keystrokes
            if keystroke.full_note in Keybinds.CURSOR
        ]
        # Returns early if no held directions
        if not held_directions:
            return
        # Sums and scales directions
        move_x, move_y = (
            sum(axis) * self.SENSITIVITY for axis in zip(*held_directions)
        )
        # Moves mouse in direction
        mouse.move(move_x, move_y, False, 0)

    def _logic_tick(self) -> bool:
        """
        Runs program logic loop. Returns false if loop should stop.
        """
        # Gets keystroke
        keystrokes = midi.get_keystrokes(self.midi_device)
        # Processes keystrokes if populated
        if keystrokes:
            for keystroke in keystrokes:
                if keystroke.full_note == Keybinds.QUIT and not self.PIANO_MODE:
                    print("\nExiting via key...")
                    return False
                self.process_keystroke(keystroke)
                # Updates display with keystroke
                self.display.update_with(keystroke, update=False)
        # Processes held cursor movements
        if not self.PIANO_MODE:
            self.process_cursor()
        # Handles closing
        if self.display.is_closed():
            print("\nExiting via display...")
            return False
        # Refreshes display
        self.display.refresh()
        self.display.tick()
        return True

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
        except KeyboardInterrupt:
            print("\nExiting via interrupt...")


def main() -> None:
    """
    Runs main controller actions.
    """
    run = True
    piano_mode = Defaults.PIANO_MODE
    key_log = Defaults.KEY_LOG
    # Argument handling
    if "--help" in sys.argv:
        run = False
        print("\nUse -p for piano mode (no controls) or -nl to turn off keylog.\n")
    # Enters piano mode
    if "-p" in sys.argv:
        piano_mode = True
        print("\nStarting in PIANO MODE. . .")
    # Disables key log
    if "-nl" in sys.argv:
        key_log = False

    # Runs program
    if run:
        program = Program(piano_mode, key_log)
        program.run()
        # Ends program
        print("\nThanks for using the keyboard swap!\n")


if __name__ == "__main__":
    main()
