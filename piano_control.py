import os
import sys

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"
import concurrent.futures
import time
from threading import Event

import keyboard
import mouse
import pygame
from pygame import midi

from packaging import Action, Keypress
from visuals import Display

# List of keyboard keybinds
KEYBOARD_KEYBINDS = {
    "A#4": "w",
    "A4": "a",
    "B4": "s",
    "C5": "d",
    "D5": " ",
    "F4": "ctrl",
    "G4": "shift",
    "G#4": "q",
    "C#5": "e",
    "E5": "f",
    "F5": "1",
    "F#5": "2",
    "G5": "3",
    "G#5": "4",
    "A5": "5",
    "A#5": "6",
    "B5": "7",
    "C6": "8",
    "C#6": "9",
    "D4": "F3",
    "D#4": "tab",
    "C#4": "esc",
}
# List of mouse click keybinds
MOUSE_KEYBINDS = {"G6": "left", "A6": "right", "G#6": "middle"}
# List of mouse direction keybinds
CURSOR_KEYBINDS = {
    # Move left
    "F6": (-1, 0),
    # Move right
    "C7": (1, 0),
    # Move up
    "A#6": (0, -1),
    # Move down
    "B6": (0, 1),
}

# Established "stop" key
STOP_KEY = "C8"

LETTERS = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

# Sets a sensitivity
SENSITIVITY = 10

# Sets modes
PIANO_MODE = False
KEY_LOG = True

# Global list of held buttons
held_directions = []

# Establishes clock
clock = pygame.time.Clock()


def read_input(midi_device: midi.Input) -> Keypress:
    """
    Attemps to read from device. Returns a keypress.
    """
    # If device returns a readable value
    if midi_device.poll():
        # Accesses event from device in format:
        # [[status,data1,data2,data3],timestamp]
        event: list[list[int], int] = midi_device.read(1)[0]  # type: ignore

        # Accesses data from event
        data = event[0]
        # If existant data:
        if data:
            # Returns a populated keypress
            return Keypress(
                letter=LETTERS[data[1] % 12],
                octave=data[1] // 12,
                velocity=data[2],
                timestamp=event[1],  # type: ignore
            )
    # If any step fails, returns an empty keypress
    return Keypress()


def process_keypress(keypress: Keypress, display: Display) -> bool:
    """
    Determines if a keypress should activate controls and display. Returns
    true if stopping.
    """
    # If empty action, returns false
    if keypress.is_empty():
        return False

    # Updates display
    display.update_display(keypress)

    # If key log is active, prints keypress
    if KEY_LOG:
        print(keypress.to_string())

    # If in piano mode, returns false
    if PIANO_MODE:
        return False

    # If in list, presses corresponding keyboard button
    if keypress.note in KEYBOARD_KEYBINDS:
        print("toggling keyboard")
        toggle_device(keypress, keyboard)
    # If in list, presses corresponding mouse button
    elif keypress.note in MOUSE_KEYBINDS:
        toggle_device(keypress, mouse)
    # If mouse direction, add/remove to/from queue
    elif keypress.note in CURSOR_KEYBINDS:
        update_held_queue(keypress)
    # Exits program if stop key is pressed
    return keypress.note == STOP_KEY


def toggle_device(keypress: Keypress, device) -> None:
    """
    Toggles device based on keypress.
    """
    # Translates note into hotkey
    hotkey = {**KEYBOARD_KEYBINDS, **MOUSE_KEYBINDS}[keypress.note]
    # Presses device hotkey
    if keypress.action == Action.PRESS:
        device.press(hotkey)
    # Releases device hotkey
    elif keypress.action == Action.RELEASE:
        device.release(hotkey)


def update_held_queue(keypress: Keypress) -> None:
    """
    Updates held queue with current keypress.
    """
    # Translates direction from keypress
    direction = CURSOR_KEYBINDS[keypress.note]
    # If a keypress PRESS action and direction not already in queue
    if keypress.action == Action.PRESS and direction not in held_directions:
        # Add direction to queue
        held_directions.append(direction)
    # If a keypress RELEASE action and direction is in queue
    elif keypress.action == Action.RELEASE and direction in held_directions:
        # Remove direction from queue
        held_directions.remove(direction)


def input_loop(midi_device: midi.Input, stop_event: Event) -> None:
    """
    Acquires button input continuously from device. Returns true if stopping.
    """
    # Creates a display object
    display = Display()

    # While stop event is npt set:
    while not stop_event.is_set():
        # Limits queries to speicifed Hz
        clock.tick(240)
        # Updates window and checks for closing
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print("Close window.")
                return
        # Reads input into keypress
        keypress = read_input(midi_device)
        # Processes button press and stops if specified
        if process_keypress(keypress, display):
            return


def cursor_loop(stop_event: Event) -> None:
    """
    Translates directions in held list into mouse movements.
    """
    # While stop event is not set:
    while not stop_event.is_set():
        # Limits queries to specified Hz
        clock.tick(60)
        # For every held direction:
        for direction in held_directions:
            # If there is no directly opposing direction:
            if (-direction[0], -direction[1]) not in held_directions:
                # Unpacks and scales x and y from direction tuple
                x, y = direction[0] * SENSITIVITY, direction[1] * SENSITIVITY
                # Moves mouse in direction
                mouse.move(x, y, False, 0)


def init_midi_devices() -> midi.Input:
    """
    Initializes and lists MIDI devices. Returns first found input device.
    """
    # Intializes MIDI
    midi.init()
    # Prints all devices
    print("\nDEVICES:")
    # For a range of all MIDI devices:
    for device_index in range(midi.get_count()):
        # Unpacks info
        device_name, device_input = device_info(device_index)
        # Prints device info
        print(f"[{device_index}] {device_name:40}", end="Type: ")
        # Determines if input or output device
        if device_input:
            print("INPUT")
        else:
            print("OUTPUT")

    # Gets ID of first input device
    input_index = midi.get_default_input_id()
    # If no device, raises error
    if input_index == -1:
        raise IndexError("No input device detected")
    # Prints device info
    print(f"\nStarting input using device: {device_info(input_index)[0]}\n")
    # Returns device
    return midi.Input(input_index)


def device_info(device_index: int) -> tuple[str, bool]:
    """
    Accesses device information. Returns tuple of name and state.
    """
    # Get info
    info: tuple[str, str, int, int, int] = midi.get_device_info(device_index)
    # Returns name and input state
    return (info[1].decode("UTF-8"), bool(info[2]))  # type:ignore


def main() -> None:
    """
    Runs main controller actions.
    """
    # Initializes midi devices and assigns input device
    midi_device = init_midi_devices()

    time.sleep(0.5)

    # Creates an event to shut down all running tasks
    stop_event = Event()

    # Opens a threading executor
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Opens thread for button input

        input_future = executor.submit(
            # Feeds multiple arguments into loop inside submit function
            lambda p: input_loop(*p),
            [midi_device, stop_event],
        )
        # Opens thread for directional processing
        cursor_future = executor.submit(cursor_loop, stop_event)

        # for future in concurrent.futures.as_completed([input_future, mouse_future]):
        #     print(repr(future.exception()))

        try:
            # While stop event has not been set:
            while not stop_event.is_set():
                time.sleep(0.2)
                # If either thread is done, stop all threads:
                if input_future.done():
                    print("Input future done.")
                    stop_event.set()
                if cursor_future.done():
                    print("Cursor future done.")
                    stop_event.set()
        # Catch keyboard interrupt exception
        except KeyboardInterrupt:
            stop_event.set()
            print("Keyboard interrupt.")


if __name__ == "__main__":

    run = True

    # Argument handling
    if "--help" in sys.argv:
        run = False
        print("\nUse -p for piano mode (no controls) or -nl to turn off keylog.\n")
    # Enters piano mode
    if "-p" in sys.argv:
        PIANO_MODE = True
        print("\nStarting in PIANO MODE. . .")
    # Disables key log
    if "-nl" in sys.argv:
        KEY_LOG = False

    if run:
        # Runs program
        main()
        # Ends program
        print("\nThanks for using the keyboard swap!\n")
