"""
## Visuals
Allows for the creation of piano display windows, to be updated with key presses.
"""

import os
import time

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"

from pathlib import Path

import pygame
from PIL import Image

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
    ) -> None:
        """
        A window display to render piano and key presses when they occur.
        """
        # Sets up display variables
        pygame.init()
        self.num_octaves = num_octaves
        self.starting_octave = starting_octave
        self.scale = scale
        self.ACTIONS = ("release", "press")
        self.NOTES = ("C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B")
        # Creates window elements
        self._clock = pygame.time.Clock()
        self.clear_memory()
        # Creates display window
        with Image.open(Paths.OCTAVE) as image:
            self._set_window_size(image.size)
        # For each action:
        for action in self.ACTIONS:
            # For each note:
            for note in self.NOTES:
                # Creates path and loads image to memory
                self._load_image(self._get_image_path(note, action), cache=True)
        # Adds a title and iconto display
        pygame.display.set_caption("Piano Display")
        pygame.display.set_icon(self._load_image(Paths.ICON, alpha=False))
        # Draws extended piano
        self.refresh()

    def _load_image(
        self, path: Path, cache: bool = False, alpha: bool = True
    ) -> pygame.Surface:
        """
        Loads image from path. Returns scaled image surface.
        """
        # Accesses if in memory
        if path in self._image_memory:
            image = self._image_memory[path]
        # Loads from image path
        else:
            try:
                image = pygame.image.load(path)
                if alpha:
                    image = pygame.Surface.convert_alpha(image)
                # Adds to memory if specified under path
            except FileNotFoundError:
                print(f"Cannot load image: {path}")
                raise SystemExit
            if cache:
                self._image_memory[path] = image
        # Gets scaled image size
        scaled_size = tuple(dimension * self.scale for dimension in image.get_size())
        # Returns scaled image
        return pygame.transform.scale(image, scaled_size)

    def _draw_element_at(
        self, image: pygame.Surface, octave: int, update: bool = False
    ) -> None:
        """
        Draws surface at specified octave.
        """
        # Creates rectangle size of octave surface at relative position
        rectangle = pygame.Rect((octave * self._octave_size[0], 0), self._octave_size)
        # Draws surface in location of rectangle
        self._window.blit(image, rectangle)
        # If specified, updates display at rectangle
        if update:
            pygame.display.update(rectangle)

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
            pygame.DOUBLEBUF,
            vsync=1,
            # pygame.RESIZABLE,
        )

    def clear_memory(self) -> None:
        """
        Clears image and keystroke memory.
        """
        self._image_memory: dict[Path, pygame.Surface] = {}
        self.held_keystrokes: set[Keystroke] = set()

    def __del__(self) -> None:
        pygame.quit()

    def update_key(self, keystroke: Keystroke) -> None:
        """
        Updates keyboard to match keystroke.
        """
        # Gets image from keystroke
        path = self._get_image_path(keystroke.note, self.ACTIONS[keystroke.press])
        # Draws key at relative octave
        self._draw_element_at(
            self._load_image(path), keystroke.octave - self.starting_octave
        )
        if keystroke not in self.held_keystrokes and keystroke.press:
            print("Adding: ", keystroke)
            self.held_keystrokes.add(keystroke)
        elif keystroke in self.held_keystrokes and not keystroke.press:
            print("Removing: ", keystroke)
            self.held_keystrokes.remove(keystroke)

    def refresh(self) -> None:
        """
        Draws piano on display screen.
        """
        # Defines octave surface
        octave_image = self._load_image(Paths.OCTAVE, cache=True)
        self._octave_size = octave_image.get_size()
        # Fills screen with black
        self._window.fill((0, 255, 0))
        # For the number of octaves defined:
        for octave in range(self.num_octaves):
            # Draws a piano octave in corresponding location
            self._draw_element_at(octave_image, octave)

        print("Held keys: ", end="")
        for keystroke in self.held_keystrokes:
            print(keystroke, end=", ")
            self.update_key(keystroke)
        print("\n")
        # Updates the full display
        pygame.display.flip()

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
    display.update_key(Keystroke(note="C", octave=5, press=True))
    time.sleep(0.5)
    display.update_key(Keystroke(note="C", octave=5, press=False))
    time.sleep(0.5)
    display.update_key(Keystroke(note="D", octave=5, press=True))
    display.update_key(Keystroke(note="F", octave=5, press=True))
    display.update_key(Keystroke(note="F#", octave=5, press=True))

    # Keeps display running until closed
    while True:

        if display.is_closed():
            break
        display.refresh()
        display.tick()
