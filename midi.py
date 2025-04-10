"""
## Midi
Provides MIDI utilities for piano typing.
"""

import os

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"
import pygame
import pygame.midi

from packaging import Keystroke

__author__ = "Ben Kraft"
__copyright__ = "None"
__credits__ = "Ben Kraft"
__license__ = "Apache"
__version__ = "0.3.0"
__maintainer__ = "Ben Kraft"
__email__ = "ben.kraft@rcn.com"
__status__ = "Prototype"


class Defaults:
    MIDI_READS = 3


def get_device(list_all: bool = True) -> pygame.midi.Input:
    """
    Initializes and lists MIDI devices. Returns first found input device.
    """
    # Intializes MIDI
    pygame.midi.init()
    # Prints all devices
    if list_all:
        print("\nDEVICES:")
        # For a range of all MIDI devices:
        for device_index in range(pygame.midi.get_count()):
            # Unpacks info
            name, is_input = get_device_info(device_index)
            device_type = "INPUT" if is_input else "OUTPUT"
            # Prints device info
            print(f"[{device_index}] {name:40} Type: {device_type}")

    # Gets ID of first input device
    input_index = pygame.midi.get_default_input_id()
    # If no device, raises error
    if input_index == -1:
        raise RuntimeError("No input device detected")
    # Prints device info
    print(f"\nStarting input using device: {get_device_info(input_index)[0]}\n")
    # Returns device
    return pygame.midi.Input(input_index)


def get_device_info(device_index: int) -> tuple[str, bool]:
    """
    Accesses device information. Returns tuple of name and state.
    """
    # Get info
    info: tuple[str, str, int, int, int] = pygame.midi.get_device_info(device_index)  # type: ignore
    # Returns name and input state
    return (info[1].decode("UTF-8"), bool(info[2]))  # type:ignore


def create_keystroke(event: list[int]) -> Keystroke:
    """
    Parses midi event into keystroke.
    """
    # Converts absolute note index to octave and relative index
    octave, note_index = divmod(event[1], len(Keystroke.NOTES))
    # Press if "velocity" is not 64
    is_press = event[2] != 64
    return Keystroke(Keystroke.NOTES[note_index], octave, is_press)


def get_keystrokes(
    midi_device: pygame.midi.Input, midi_reads: int = Defaults.MIDI_READS
) -> list[Keystroke]:
    """
    Attempts to read a specified number of MIDI events from the device. Filters
    out clock events and empty velocities, then returns the corresponding keystrokes.

    Args:
        midi_device: A pygame.midi.Input instance representing the MIDI input device.
        midi_reads: The number of events to read from the device at once.

    Returns:
        A list of Keystroke objects parsed from the MIDI events.
    """
    try:
        # Returns early if device has no events
        if not midi_device.poll():
            return []
        # Accesses events from device in format:
        # [[[status, note, velocity, data_3], timestamp], ...]
        midi_events: list[list[list[int], int]] = midi_device.read(midi_reads)  # type: ignore
        # Strips timestamp
        untimed_events = [event[0] for event in midi_events]
        # Filters out clock events and empty velocities and parses into keystrokes
        return [
            create_keystroke(event)
            for event in untimed_events
            if event[0] != 248 and event[2] != 0
        ]

    except Exception as e:
        print(f"Error: {e}")
        return []
