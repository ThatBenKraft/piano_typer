"""
## Visuals
Allows for the creation of piano display windows, to be updated with key presses.
"""

import os
import time

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"

from pathlib import Path

import pygame

from packaging import Keypress

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
    SCALE = 1
    FRAME_RATE = 120


class Paths:
    """
    Paths used for display.
    """

    ASSETS = Path(__file__).parent / "assets"
    OCTAVE = ASSETS / "octave.png"
    ICON = ASSETS / "icon.png"


class Display:
    """
    A window display to render piano and key presses when they occur.
    """

    def __init__(
        self,
        num_octaves: int = Defaults.NUM_OCTAVES,
        starting_octave: int = Defaults.STARTING_OCTAVE,
        scale: float = Defaults.SCALE,
        flourish: bool = True,
    ) -> None:
        """
        A window display to render piano and key presses when they occur.
        """
        # Sets display constants
        pygame.init()
        self.NUM_OCTAVES = num_octaves
        self.STARTING_OCTAVE = starting_octave
        self.scale = scale
        self.ACTIONS = ("release", "press")
        self.NOTES = ("C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B")
        self._clock = pygame.time.Clock()
        self.clear_memory()
        # Adds a title to display
        pygame.display.set_caption("Piano Display")
        # Loads window icon
        pygame.display.set_icon(self.load_image(Paths.ICON))
        # Loads all key images into memory
        self._load_key_images()
        # Draws extended piano
        self.refresh(flourish, resize=True)

    def __del__(self) -> None:
        pygame.quit()

    def load_image(self, path: Path, cache: bool = False) -> pygame.Surface:
        """
        Loads image from path.
        """
        if path in self.image_memory:
            # Returns scaled image
            return self._scale_image(self.image_memory[path])
        else:
            image = pygame.image.load(path)
            # Adds to memory if specified under path
            if cache:
                self.image_memory[path] = image
            return self._scale_image(image)

    def _scale_image(self, image: pygame.Surface) -> pygame.Surface:
        """
        Scales image by factor.
        """
        new_dimensions = tuple(dimension * self.scale for dimension in image.get_size())
        return pygame.transform.scale(image, new_dimensions)

    def _load_key_images(self) -> None:
        """
        Loads all key images into memory.
        """
        # For each action:
        for action in self.ACTIONS:
            # For each note:
            for note in self.NOTES:
                # Creates path and loads image to memory
                self.load_image(Paths.ASSETS / action / f"{note}.png", cache=True)

    def clear_memory(self) -> None:
        """
        Clears image memory.
        """
        self.image_memory: dict[Path, pygame.Surface] = {}

    def refresh(self, flourish: bool = False, resize: bool = False) -> None:
        """
        Draws piano on display screen.
        """
        # Defines octave surface
        octave_image = self.load_image(Paths.OCTAVE, cache=True)
        # Sets a display window with image's size
        if resize:
            self.window = pygame.display.set_mode(
                (
                    octave_image.get_width() * self.NUM_OCTAVES,
                    octave_image.get_height(),
                ),
                pygame.RESIZABLE,
            )
        # Fills screen with black
        self.window.fill((255, 255, 255))
        # For the number of octaves defined:
        for octave in range(self.NUM_OCTAVES):
            # If flourishing, spaces out octave draws to fill 1 second
            if flourish:
                time.sleep(0.5 / self.NUM_OCTAVES)
            # Draws a piano octave in corresponding location
            self._draw_element_at(octave_image, octave, update=flourish)
        # Updates the full display
        pygame.display.flip()

    def update_key(self, keypress: Keypress) -> None:
        """
        Updates keyboard to match keypress.
        """
        # Defines action
        action = self.ACTIONS[keypress.press]
        # Draws key at relative octave
        self._draw_element_at(
            self.load_image(Paths.ASSETS / action / f"{keypress.note}.png"),
            keypress.octave - self.STARTING_OCTAVE,
        )

    def _draw_element_at(
        self, image: pygame.Surface, octave: int, update: bool = True
    ) -> None:
        """
        Draws surface at specified octave.
        """
        # Creates rectangle size of octave surface at relative position
        rectangle = pygame.Rect((octave * image.get_width(), 0), image.get_size())
        # Draws surface in location of rectangle
        self.window.blit(image.convert_alpha(), rectangle)
        # If specified, updates display at rectangle
        if update:
            pygame.display.update(rectangle)

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
        self._clock.tick(frame_rate)


if __name__ == "__main__":
    # Creates a display
    display = Display()

    time.sleep(0.5)
    keypress = Keypress(note_index=0, octave=5)
    display.update_key(keypress)
    time.sleep(0.5)
    keypress = Keypress(note_index=0, octave=5, press=False)
    display.update_key(keypress)

    # Keeps display running until closed
    while True:

        display.tick()
        display.refresh()
        if display.is_closed():
            break
