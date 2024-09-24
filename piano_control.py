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

from packaging import NOTES, Keystroke
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

# Sets a sensitivity
SENSITIVITY = 11

# Sets modes
PIANO_MODE = False
KEY_LOG = True

# Global list of held buttons
held_directions = []

# Establishes clock
clock = pygame.time.Clock()


def read_input(midi_device: midi.Input) -> Keystroke | None:
    """
    Attemps to read from device. Returns a keystroke.
    """
    # If device returns a readable value
    if not midi_device.poll():
        return
    # Accesses event from device in format:
    # [[status,data1,data2,data3],timestamp]
    event: list[list[int], int] = midi_device.read(1)[0]  # type: ignore
    # Accesses data from event
    inner_data = event[0]
    # Returns None if no data
    if not inner_data:
        return
    # Determines action from velocity
    match inner_data[2]:
        case 0:
            return
        case 64:
            press = False
        case _:
            press = True
    # Returns a populated keystroke
    return Keystroke(NOTES[inner_data[1] % 12], inner_data[1] // 12, press)


def process_keystroke(keystroke: Keystroke) -> bool:
    """
    Determines if a keystroke should activate controls and display. Returns
    true if stopping.
    """
    # If key log is active, prints keystroke
    if KEY_LOG and keystroke:
        print(str(keystroke))
    # If in piano mode, returns false
    if PIANO_MODE:
        return False

    # If in list, presses corresponding keyboard button
    if keystroke.full_note in KEYBOARD_KEYBINDS:
        toggle_device(keystroke, keyboard)
    # If in list, presses corresponding mouse button
    elif keystroke.full_note in MOUSE_KEYBINDS:
        toggle_device(keystroke, mouse)
    # If mouse direction, add/remove to/from queue
    elif keystroke.full_note in CURSOR_KEYBINDS:
        update_held_queue(keystroke)
    # Exits program if stop key is pressed
    return keystroke.full_note == STOP_KEY


def toggle_device(keystroke: Keystroke, device) -> None:
    """
    Toggles device based on keystroke.
    """
    # Translates note into hotkey
    hotkey = {**KEYBOARD_KEYBINDS, **MOUSE_KEYBINDS}[keystroke.full_note]
    # Presses or releases device hotkey
    device.press(hotkey) if keystroke.press else device.release(hotkey)


def update_held_queue(keystroke: Keystroke) -> None:
    """
    Updates held queue with current keystroke.
    """
    # Translates direction from keystroke
    direction = CURSOR_KEYBINDS[keystroke.full_note]
    # If a keystroke PRESS action and direction not already in queue
    if keystroke.press and direction not in held_directions:
        # Add direction to queue
        held_directions.append(direction)
    # If a keystroke RELEASE action and direction is in queue
    elif not keystroke.press and direction in held_directions:
        # Remove direction from queue
        held_directions.remove(direction)


def input_loop(midi_device: midi.Input, stop_event: Event) -> None:
    """
    Acquires button input continuously from device. Returns true if stopping.
    """
    # Creates a display object
    display = Display()

    # While stop event is not set:
    while not stop_event.is_set():
        # Limits queries to speicifed Hz
        clock.tick(120)
        # Updates window and checks for closing
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print("\nClosed window.")
                return
        # Reads input into keystroke
        keystroke = read_input(midi_device)
        if keystroke:
        # Updates display
            display.update_key(keystroke)
            # Processes button press and breaks if specified
            if process_keystroke(keystroke):
                break


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
        print(f"[{device_index}] {device_name:40} Type: {"INPUT" if device_input else "OUTPUT"}")

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
    info: tuple[str, str, int, int, int] = midi.get_device_info(device_index)  # type: ignore
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
        # PIANO_MODE = True

        main()
        # Ends program
        print("\nThanks for using the keyboard swap!\n")
