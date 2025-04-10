"""
### Piano Export
A small module used to manipulate, animate, and export frames from a `Display`
as .png's, .gif's, etc.
"""

import os
import shutil
from collections import deque
from pathlib import Path

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"

import pygame
from PIL import Image

from packaging import Keystroke
from visuals import Display, Paths

__author__ = "Ben Kraft"
__copyright__ = "None"
__credits__ = "Ben Kraft"
__license__ = "Apache"
__version__ = "0.1.0"
__maintainer__ = "Ben Kraft"
__email__ = "ben.kraft@rcn.com"
__status__ = "Prototype"

EXPORT_DIRECTORY_PATH = Paths.ASSETS / "export"

NUM_KEYS_PRESSED = 25

SAVE_IMAGES = False
FRAMES_PER_SECOND = 50
MILLISECONDS_PER_FRAME = 1000 / FRAMES_PER_SECOND
if MILLISECONDS_PER_FRAME < 20:
    raise ValueError("FPS too high!")

index = 0


def main() -> None:
    """
    Exports animation as gif under specified path.
    """
    display = Display(num_octaves=6, scale=1)
    frames: list[Image.Image] = []

    empty_directory(EXPORT_DIRECTORY_PATH)

    # return
    keystroke_history: deque[Keystroke] = deque([], maxlen=NUM_KEYS_PRESSED)

    # For each octave:
    for octave in range(display.num_octaves):
        # For each note index:
        for note in Keystroke.NOTES:
            # Creates keystroke
            keystroke = Keystroke(note, octave + display.starting_octave)
            # If keystroke history is full:
            if len(keystroke_history) == NUM_KEYS_PRESSED:
                # Accesses and inverts keystroke from DISTANCE ago
                display.draw_keystroke(keystroke_history[0].inverted())
            # Updates display with keystroke
            display.draw_keystroke(keystroke)
            # Adds window image to frames
            frames.append(get_image(display))
            # Adds keystroke to history
            keystroke_history.append(keystroke)

    # For each keystroke in remaining history:
    for keystroke in keystroke_history:
        # Updates display with keystroke
        display.draw_keystroke(keystroke.inverted())
        # Adds window image to frames
        frames.append(get_image(display))

    export_as_gif(frames, EXPORT_DIRECTORY_PATH / "demo.gif")

    frames.reverse()

    export_as_gif(frames, EXPORT_DIRECTORY_PATH / "demo_reversed.gif")


def export_as_gif(frames: list[Image.Image], path: Path) -> None:
    """
    Exports frames as gif under specified path.
    """
    frames[0].save(
        path,
        save_all=True,
        append_images=frames[1:],
        duration=MILLISECONDS_PER_FRAME,
        loop=0,
    )


def get_image(display: Display, save_image: bool = SAVE_IMAGES) -> Image.Image:
    """
    Gets current window image and saves if specified.
    """
    # Converts display surface to string
    string_data = pygame.image.tostring(display._window, "RGBA")
    # Creates image from string
    image = Image.frombytes("RGBA", display._window.get_size(), string_data)
    # Saves image if specified
    if save_image:
        global index
        image.save(EXPORT_DIRECTORY_PATH / f"{index:04}.png")
        index += 1
    return image


def empty_directory(directory_path: Path) -> None:
    """
    Empties directory if it exists.
    """
    try:
        # Check if the directory exists
        if directory_path.exists() and directory_path.is_dir():
            # Iterate over all items in the directory
            for item in directory_path.iterdir():
                # Check if the item is a file or a symbolic link
                if item.is_file() or item.is_symlink():
                    item.unlink()
                    print(f"File '{item.name}' deleted.")
                # If the item is a directory, remove it recursively
                elif item.is_dir():
                    shutil.rmtree(item)  # Remove directory and its contents
                    print(f"Directory '{item.name}' deleted.")
            print(f"Directory '{directory_path.name}' is now empty.")
        else:
            print(f"Directory '{directory_path.name}' does not exist.")

    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
