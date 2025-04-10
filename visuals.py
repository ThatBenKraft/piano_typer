"""
### Visuals
Allows for the creation of piano display windows, to be updated with key presses.
"""

import itertools
import os
import time
from pathlib import Path

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"
import pygame

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
    """
    Default values for piano display.
    """

    NUM_OCTAVES = 5
    STARTING_OCTAVE = 3
    SCALE = 1
    FRAMERATE = 60
    BACKGROUND_COLOR = (0, 255, 0)


class Paths:
    """
    Paths used for display.
    """

    ASSETS = Path(__file__).parent / "assets"
    OCTAVE = ASSETS / "octave.png"
    ICON = ASSETS / "icon.png"


class Display:
    """
    A window display to render a piano and key presses when they occur.

    Attributes:
        num_octaves: Number of octaves in the piano display.
        starting_octave: The first octave to be shown.
        scale: Scale factor for resizing images.
        background_color: RGB tuple of the display's background color.
    """

    def __init__(
        self,
        num_octaves: int = Defaults.NUM_OCTAVES,
        starting_octave: int = Defaults.STARTING_OCTAVE,
        scale: float = Defaults.SCALE,
        background_color: tuple[int, int, int] = Defaults.BACKGROUND_COLOR,
    ) -> None:
        """
        Initializes the display window and loads necessary assets.

        Args:
            num_octaves: Number of octaves in the piano display.
            starting_octave: The first octave to be shown.
            scale: Scale factor for resizing images.
            background_color: RGB tuple of the display's background color.
        """
        # Sets up display variables
        pygame.init()
        self.num_octaves = num_octaves
        self.starting_octave = starting_octave
        self.scale = scale
        self.background_color = background_color
        self.clear_memory()

        # Initializes window
        self._set_window_size((1, 1))
        # Loads key images to memory preemptively
        for note, action in itertools.product(Keystroke.NOTES, Keystroke.ACTIONS):
            self._load_image(self._get_image_path(note, action))
        # Adds a title and iconto display
        pygame.display.set_caption("Piano Display")
        pygame.display.set_icon(
            self._load_image(Paths.ICON, do_scale=False, do_cache=False)
        )
        # Draws extended piano
        self.refresh(resize=True)

    def clear_memory(self) -> None:
        """
        Clears image and keystroke memory.
        """
        # Under its path, each image is stored with its scale.
        self._image_memory: dict[Path, pygame.Surface] = {}

    def _load_image(
        self, path: Path, do_scale: bool = True, do_cache: bool = True
    ) -> pygame.Surface:
        """
        Loads image from path. Returns scaled image surface.
        """
        # Acquires image if it is already in memory
        if path in self._image_memory:
            image = self._image_memory[path]
        # Loads from image path
        else:
            try:
                image = pygame.image.load(path).convert_alpha()
            except FileNotFoundError:
                print(f"Cannot load image: {path}")
                raise SystemExit
            # Adds to memory if specified
            if do_cache:
                self._image_memory[path] = image
        # Gets scaled image size
        image_size = image.get_size()
        scaled_size = tuple(dimension * self.scale for dimension in image_size)
        # Returns scaled image
        return pygame.transform.scale(image, scaled_size if do_scale else image_size)

    def _draw_image_at(
        self, image: pygame.Surface, octave: int, update: bool = True
    ) -> None:
        """
        Draws surface at specified octave. Updates surface if specified.
        """
        octave_size = self._load_image(Paths.OCTAVE).get_size()
        # Creates rectangle size of octave surface at relative position
        rectangle = pygame.Rect((octave * octave_size[0], 0), octave_size)
        # Draws surface in location of rectangle
        self._window.blit(image, rectangle)
        # If specified, updates display at rectangle
        if update:
            pygame.display.update(rectangle)

    def draw_keystroke(self, keystroke: Keystroke, update: bool = True) -> None:
        """
        Draws key on display. Updates surface if specified.
        """
        # Gets image from keystroke
        action = Keystroke.ACTIONS[keystroke.is_press]
        path = self._get_image_path(keystroke.note, action)
        octave = keystroke.octave - self.starting_octave
        # Draws key at relative octave
        self._draw_image_at(self._load_image(path), octave, update)

    def _get_image_path(self, note: str, action: str) -> Path:
        """
        Returns path of image corresponding to note and action.
        """
        return Paths.ASSETS / action / f"{note}.png"

    def _set_window_size(self, octave_size: tuple[int, ...]) -> None:
        """
        Sets display window size from octave size.
        """
        self._window = pygame.display.set_mode(
            (octave_size[0] * self.num_octaves, octave_size[1]),
            # pygame.RESIZABLE,
        )

    def set_scale(self, scale: float, held_keystrokes: set[Keystroke] = set()) -> None:
        """
        Sets scale of window.
        """
        self.scale = scale
        self.refresh(held_keystrokes, resize=True)

    def refresh(
        self, held_keystrokes: set[Keystroke] = set(), resize: bool = False
    ) -> None:
        """
        Redraws piano and held keys on display screen.
        """
        # Gets base octave image
        octave_image = self._load_image(Paths.OCTAVE)
        # Resizes window if specified
        if resize:
            self._set_window_size(octave_image.get_size())
        # Fills screen with background color
        self._window.fill(self.background_color)
        # Draws base piano
        for octave in range(self.num_octaves):
            self._draw_image_at(octave_image, octave, update=False)
        # Draws all held keys
        for keystroke in held_keystrokes:
            self.draw_keystroke(keystroke, update=False)
        # Updates the full display
        pygame.display.flip()

    def __del__(self) -> None:
        self.close()

    def close(self) -> None:
        pygame.quit()

    def is_closed(self) -> bool:
        """
        Returns true if window is closed.
        """
        # For every event in pygame:
        if pygame.event.peek(pygame.QUIT):
            return True
        # Otherwise, return false
        return False


if __name__ == "__main__":
    # Creates a display
    display = Display(scale=0.5)
    clock = pygame.time.Clock()

    time.sleep(0.5)
    display.draw_keystroke(Keystroke("C", 5))
    time.sleep(0.5)
    display.draw_keystroke(Keystroke("C", 5, is_press=False))
    time.sleep(0.5)
    display.draw_keystroke(Keystroke("D", 5))
    display.draw_keystroke(Keystroke("F", 5))
    display.draw_keystroke(Keystroke("F#", 5))
    display.draw_keystroke(Keystroke("A", 4))
    time.sleep(0.5)

    held_keys = {Keystroke("C", 5), Keystroke("E", 5), Keystroke("G", 5)}
    display.refresh(held_keys)
    time.sleep(0.5)

    display.set_scale(0.5, held_keys)
    time.sleep(0.5)

    display.set_scale(0.25, held_keys)
    time.sleep(0.5)

    # Keeps display running until closed
    while True:

        if display.is_closed():
            break
        display.refresh(held_keys)
        clock.tick(Defaults.FRAMERATE)
