"""
### Visuals
Allows for the creation of piano display windows, to be updated with key presses.
"""

import os
import time
from pathlib import Path

from PIL import Image

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"
import pygame

from packaging import Keystroke

__author__ = "Ben Kraft"
__copyright__ = "None"
__credits__ = "Ben Kraft"
__license__ = "Apache"
__version__ = "0.2.2"
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
    FRAME_RATE = 60
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
        self._clock = pygame.time.Clock()
        self.clear_memory()

        with Image.open(Paths.OCTAVE) as image:
            self._set_window_size(image.size)
        # Loads key images to memory preemptively
        for action in Keystroke.ACTIONS:
            for note in Keystroke.NOTES:
                self._load_image(self._get_image_path(note, action), cache=True)
        # Adds a title and iconto display
        pygame.display.set_caption("Piano Display")
        pygame.display.set_icon(self._load_image(Paths.ICON))
        # Draws extended piano
        self.refresh()

    def clear_memory(self) -> None:
        """
        Clears image and keystroke memory.
        """
        self._image_memory: dict[Path, pygame.Surface] = {}
        self.held_keystrokes: set[Keystroke] = set()

    def _load_image(self, path: Path, cache: bool = False) -> pygame.Surface:
        """
        Loads image from path. Returns scaled image surface.
        """
        # Accesses if in memory
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
            if cache:
                self._image_memory[path] = image
        # Gets scaled image size
        scaled_size = tuple(dimension * self.scale for dimension in image.get_size())
        # Returns scaled image
        return pygame.transform.scale(image, scaled_size)

    def _draw_image_at(
        self, image: pygame.Surface, octave: int, update: bool = False
    ) -> None:
        """
        Draws surface at specified octave. Updates surface if specified.
        """
        # Creates rectangle size of octave surface at relative position
        rectangle = pygame.Rect((octave * self._octave_size[0], 0), self._octave_size)
        # Draws surface in location of rectangle
        self._window.blit(image, rectangle)
        # If specified, updates display at rectangle
        if update:
            pygame.display.update(rectangle)

    def _draw_keystroke(self, keystroke: Keystroke, update: bool = False) -> None:
        """
        Draws key on display. Updates surface if specified.
        """
        # Gets image from keystroke
        path = self._get_image_path(keystroke.note, Keystroke.ACTIONS[keystroke.press])
        # Draws key at relative octave
        self._draw_image_at(
            self._load_image(path), keystroke.octave - self.starting_octave, update
        )

    def update_key(self, keystroke: Keystroke, update: bool = True) -> None:
        """
        Updates held keystrokes with new keystroke. Updates surface if specified.
        """
        # Adds or removes from held keys
        if keystroke not in self.held_keystrokes and keystroke.press:
            self.held_keystrokes.add(keystroke)
        elif keystroke in self.held_keystrokes and not keystroke.press:
            self.held_keystrokes.remove(keystroke)
        # Draws individual keystroke
        self._draw_keystroke(keystroke, update)

    def _get_image_path(self, note: str, action: str) -> Path:
        """
        Returns path of image corresponding to note and action.
        """
        return Paths.ASSETS / action / f"{note}.png"

    def _set_window_size(self, octave_size: tuple[int, int]) -> None:
        """
        Sets display window size from octave size.
        """
        self._window = pygame.display.set_mode(
            (octave_size[0] * self.num_octaves, octave_size[1]),
            # pygame.RESIZABLE,
        )

    def refresh(self) -> None:
        """
        Draws piano and keys on display screen.
        """
        # Defines octave surface
        octave_image = self._load_image(Paths.OCTAVE, cache=True)
        self._octave_size = octave_image.get_size()
        # Fills screen with background color
        self._window.fill(self.background_color)
        # Draws base piano
        for octave in range(self.num_octaves):
            self._draw_image_at(octave_image, octave)
        # Draws all held keys
        for keystroke in self.held_keystrokes:
            self._draw_keystroke(keystroke)
        # Updates the full display
        pygame.display.flip()

    def tick(self, frame_rate: int = Defaults.FRAME_RATE) -> None:
        """
        Delays by amount of time nessesary to maintain specified frame rate.
        """
        self._clock.tick(frame_rate)

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
    display = Display()

    time.sleep(0.5)
    display.update_key(Keystroke("C", 5))
    time.sleep(0.5)
    display.update_key(Keystroke("C", 5, press=False))
    time.sleep(0.5)
    display.update_key(Keystroke("D", 5))
    display.update_key(Keystroke("F", 5))
    display.update_key(Keystroke("F#", 5))
    display.update_key(Keystroke("A", 4))

    # Keeps display running until closed
    while True:

        if display.is_closed():
            break
        display.refresh()
        display.tick()
