"""
## Visuals
Allows for the creation of piano display windows, to be updated with key presses.
"""

import os
import time

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"

from pathlib import Path

import pygame

from packaging import Action, Keypress

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
    ) -> None:
        """
        A window display to render piano and key presses when they occur.
        """
        # Sets display constants
        self.NUM_OCTAVES = num_octaves
        self.STARTING_OCTAVE = starting_octave
        self.SCALE = scale
        # Defines octave surface
        octave_surface = pygame.image.load(octave_image)
        # Acquires scaled sizes from surface
        self.octave_width, self.octave_height = (
            dimension * self.SCALE for dimension in octave_surface.get_size()
        )
        # Creates scaled octave surface
        self.scaled_octave_surface = pygame.transform.scale(
            octave_surface, (self.octave_width, self.octave_height)
        )
        # Sets a display window with image's size
        self.window = pygame.display.set_mode(
            (self.octave_width * self.NUM_OCTAVES, self.octave_height)
        )
        # Adds a title to display
        pygame.display.set_caption("Piano Display")
        # Loads window icon
        pygame.display.set_icon(pygame.image.load(Paths.ICON))
        # Draws extended piano
        self.refresh(flourish=True)

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
                time.sleep(1 / self.NUM_OCTAVES)
            # Draws a piano octave in corresponding location
            self._draw_element_at(self.scaled_octave_surface, i, flourish)
        # Updates the full display
        pygame.display.flip()

    def update_key(self, keypress: Keypress) -> None:
        """
        Updates keyboard to match keypress.
        """
        # Returns early if keypress is empty
        if keypress.is_empty():
            return
        # Creates path to key image
        key_image = (
            Paths.ASSETS / keypress.action.name.lower() / f"{keypress.letter}.png"
        )
        # Creates scaled surface from image
        scaled_key_surface = pygame.transform.scale(
            pygame.image.load(key_image).convert_alpha(),
            (self.octave_width, self.octave_height),
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
            (octave_num * self.octave_width, 0),  # (x, y)
            (self.octave_width, self.octave_height),  # (width, height)
        )
        # Draws surface in location of rectangle
        self.window.blit(surface, octave_rectangle)
        # If specified, updates display at rectangle
        if update:
            pygame.display.update(octave_rectangle)


if __name__ == "__main__":
    # Initializes pygame
    pygame.init()
    # Creates a display
    display = Display(Paths.ASSETS / "octave.png")

    # time.sleep(0.5)
    # keypress = Keypress(letter="a", octave=5, action=Action.PRESS)
    # display.update_key(keypress)
    # time.sleep(0.5)
    # keypress = Keypress(letter="a", octave=5, action=Action.RELEASE)
    # display.update_key(keypress)

    # Keeps display running until closed
    run = True
    while run:
        pygame.time.Clock().tick(60)
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
    # Closes pygame
    pygame.quit()
