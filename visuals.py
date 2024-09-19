"""
## Visuals
Allows for the creation of piano display windows, to be updated with key presses.
"""

import os
import time

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"

from pathlib import Path

import pygame

from packaging import NOTES, Keypress

__author__ = "Ben Kraft"
__copyright__ = "None"
__credits__ = "Ben Kraft"
__license__ = "Apache"
__version__ = "0.2.0"
__maintainer__ = "Ben Kraft"
__email__ = "ben.kraft@rcn.com"
__status__ = "Prototype"


class Defaults:
    """
    Default values for piano display.
    """

    NUM_OCTAVES = 5
    STARTING_OCTAVE = 3
    SCALE = 1.0
    FRAME_RATE = 60


class Paths:
    """
    Paths used for display.
    """

    ASSETS = Path(__file__).parent / "assets"
    ICON = ASSETS / "icon.png"


class Display:
    """
    A window display to render piano and key presses when they occur.
    """

    def __init__(
        self,
        octave_image: Path,
        num_octaves: int = Defaults.NUM_OCTAVES,
        starting_octave: int = Defaults.STARTING_OCTAVE,
        scale: float = Defaults.SCALE,
        flourish: bool = True,
    ) -> None:
        """
        A window display to render piano and key presses when they occur.
        """
        # Defines octave surface
        octave_surface = pygame.image.load(octave_image)
        # Sets display constants
        self.NUM_OCTAVES = num_octaves
        self.STARTING_OCTAVE = starting_octave
        self.SCALE = scale
        # Acquires scaled sizes from surface
        self._octave_width, self._octave_height = (
            dimension * self.SCALE for dimension in octave_surface.get_size()
        )
        # Creates scaled octave surface
        self._scaled_octave_surface = pygame.transform.scale(
            octave_surface, (self._octave_width, self._octave_height)
        )
        # Sets a display window with image's size
        self.window = pygame.display.set_mode(
            (self._octave_width * self.NUM_OCTAVES, self._octave_height)
        )
        # Loads all key images into memory
        self._load_key_images()
        # Adds a title to display
        pygame.display.set_caption("Piano Display")
        # Loads window icon
        pygame.display.set_icon(pygame.image.load(Paths.ICON))
        # Draws extended piano
        self.refresh(flourish)

    def _load_key_images(self) -> None:
        """
        Loads all key images into memory.
        """
        # Initializes dictionary
        self._key_images: dict[str, list[pygame.Surface]] = {"press": [], "release": []}
        # For each action:
        for action in self._key_images:
            # For each note:
            for note in NOTES:
                # Defines path and loads image
                path = Paths.ASSETS / action / f"{note}.png"
                image = pygame.image.load(path).convert_alpha()
                # Adds image to corresponding list
                self._key_images[action].append(image)

    def refresh(self, flourish: bool = False) -> None:
        """
        Draws piano on display screen.
        """
        # Fills screen with black
        self.window.fill((255, 255, 255))
        # For the number of octaves defined:
        for i in range(self.NUM_OCTAVES):
            # If flourishing, spaces out octave draws to fill 1 second
            if flourish:
                time.sleep(0.5 / self.NUM_OCTAVES)
            # Draws a piano octave in corresponding location
            self._draw_element_at(self._scaled_octave_surface, i, flourish)
        # Updates the full display
        pygame.display.flip()

    def update_key(self, keypress: Keypress) -> None:
        """
        Updates keyboard to match keypress.
        """
        # Defines action
        action = "press" if keypress.press else "release"
        # Creates scaled surface from image
        scaled_key_surface = pygame.transform.scale(
            self._key_images[action][keypress.note_index],
            (self._octave_width, self._octave_height),
        )
        # Draws key at relative octave
        self._draw_element_at(
            scaled_key_surface, keypress.octave - self.STARTING_OCTAVE
        )

    def _draw_element_at(
        self, surface: pygame.Surface, octave_num: int, update: bool = True
    ) -> None:
        """
        Draws surface at specified octave.
        """
        # Creates rectangle size of octave surface at relative position
        octave_rectangle = pygame.Rect(
            (octave_num * self._octave_width, 0),  # (x, y)
            (self._octave_width, self._octave_height),  # (width, height)
        )
        # Draws surface in location of rectangle
        self.window.blit(surface, octave_rectangle)
        # If specified, updates display at rectangle
        if update:
            pygame.display.update(octave_rectangle)

    def is_closed(self) -> bool:
        """
        Returns true if window is closed.
        """
        # For every event in pygame:
        for event in pygame.event.get():
            # If event is quit, return true
            if event.type == pygame.QUIT:
                return True
        # Otherwise, return false
        return False

    def tick(self, frame_rate: int = Defaults.FRAME_RATE) -> None:
        """
        Delays by amount of time nessesary to maintain specified frame rate.
        """
        pygame.time.Clock().tick(frame_rate)


if __name__ == "__main__":
    # Initializes pygame
    pygame.init()
    # Creates a display
    display = Display(Paths.ASSETS / "octave.png")

    time.sleep(0.5)
    keypress = Keypress(note_index=0, octave=5)
    display.update_key(keypress)
    time.sleep(0.5)
    keypress = Keypress(note_index=0, octave=5, press=False)
    display.update_key(keypress)

    # Keeps display running until closed
    closed = False
    while not closed:

        display.tick()
        closed = display.is_closed()

    # Closes pygame
    pygame.quit()
