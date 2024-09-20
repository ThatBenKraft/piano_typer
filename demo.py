import os
import shutil
from collections import deque
from pathlib import Path

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"

import pygame
from PIL import Image

from packaging import NOTES, Keypress
from visuals import Display, Paths

EXPORT_DIRECTORY_PATH = Paths.ASSETS / "export"

NUM_KEYS_PRESSED = 25

SAVE_IMAGES = False
FRAMES_PER_SECOND = 50
MILLISECONDS_PER_FRAME = 1000 / FRAMES_PER_SECOND
if MILLISECONDS_PER_FRAME < 20:
    raise ValueError("FPS too high!")

index = 0


def main() -> None:

    display = Display(num_octaves=6, scale=1, flourish=False)

    frames: list[Image.Image] = []

    empty_directory(EXPORT_DIRECTORY_PATH)

    # return
    keypress_history: deque[Keypress] = deque([], maxlen=NUM_KEYS_PRESSED)

    # For each octave:
    for octave in range(display.NUM_OCTAVES):
        # For each note index:
        for note_index in range(len(NOTES)):
            # Creates keypress
            keypress = Keypress(note_index, octave + display.STARTING_OCTAVE)
            # If keypress history is full:
            if len(keypress_history) == NUM_KEYS_PRESSED:
                # Accesses and inverts keypress from DISTANCE ago
                display.update_key(keypress_history[0].inverted())
            # Updates display with keypress
            display.update_key(keypress)
            # Adds window image to frames
            frames.append(get_image(display))
            # Adds keypress to history
            keypress_history.append(keypress)

    # For each keypress in remaining history:
    for keypress in keypress_history:
        # Updates display with keypress
        display.update_key(keypress.inverted())
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
    string_data = pygame.image.tostring(display.window, "RGBA")
    # Creates image from string
    image = Image.frombytes("RGBA", display.window.get_size(), string_data)
    # Saves image if specified
    if save_image:
        global index
        image.save(EXPORT_DIRECTORY_PATH / f"{index:04}.png")
        index += 1
    return image


def empty_directory(directory_path: Path) -> None:
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
