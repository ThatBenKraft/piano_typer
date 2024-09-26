"""
## Midi
Provides MIDI utilities for piano typing.
"""

import os

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"
from pygame import midi

from packaging import NOTES, Keystroke


class Defaults:
    MIDI_READS = 3

def get_device(list_all: bool = True) -> midi.Input:
    """
    Initializes and lists MIDI devices. Returns first found input device.
    """
    # Intializes MIDI
    midi.init()
    # Prints all devices
    if list_all:
        print("\nDEVICES:")
        # For a range of all MIDI devices:
        for device_index in range(midi.get_count()):
            # Unpacks info
            name, is_input = get_device_info(device_index)
            # Prints device info
            print(f"[{device_index}] {name:40} Type: {"INPUT" if is_input else "OUTPUT"}")

    # Gets ID of first input device
    input_index = midi.get_default_input_id()
    # If no device, raises error
    if input_index == -1:
        raise IndexError("No input device detected")
    # Prints device info
    print(f"\nStarting input using device: {get_device_info(input_index)[0]}\n")
    # Returns device
    return midi.Input(input_index)

def get_device_info(device_index: int) -> tuple[str, bool]:
    """
    Accesses device information. Returns tuple of name and state.
    """
    # Get info
    info: tuple[str, str, int, int, int] = midi.get_device_info(device_index)  # type: ignore
    # Returns name and input state
    return (info[1].decode("UTF-8"), bool(info[2]))  # type:ignore

def parse_event(event: list[int]) -> Keystroke:
    """
    Parses midi event into keystroke.
    """
    note_index = event[1]
    velocity = event[2]
    return Keystroke(NOTES[note_index % 12], note_index // 12, velocity != 64)

def get_keystrokes(midi_device: midi.Input, midi_reads: int = Defaults.MIDI_READS) -> list[Keystroke]:
    """
    Attemps to read events from device, `midi_read`'s at a time. Returns a list 
    of keystrokes.
    """
    # Returns early if device has no events
    if not midi_device.poll():
        return []
    # Accesses events from device in format:
    # [[[status, note, velocity, data_3], timestamp], ...]
    midi_events: list[list[list[int], int]] = midi_device.read(midi_reads)  # type: ignore
    # Strips timestamp
    untimed_events = [event[0] for event in midi_events]
    # Filters out clock events and empty velocities
    filtered_events = [
        event for event in untimed_events if event[0] != 248 and event[2] != 0
    ]
    # Parses event lists into keystrokes
    return [parse_event(event) for event in filtered_events]
