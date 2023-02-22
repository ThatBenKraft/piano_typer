import os

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"

import pygame
from PIL import Image as image_data

from packaging import Keypress

# Sets number of used octaves
NUM_OCTAVES = 5
# Sets starting octave
STARTING_OCTAVE = 3


class Display:
    """
    A display to render piano and key presses when they occur.
    """

    def __init__(self) -> None:
        # Acquires sizes from image
        with image_data.open(self._get_path("piano")) as image:
            self.piano_width, self.window_height = image.size
        # Creates window width from number of octaves
        self.window_width = self.piano_width * NUM_OCTAVES
        # Sets a display window with image's size
        self.window = pygame.display.set_mode([self.window_width, self.window_height])
        # Adds a title and icon to display
        pygame.display.set_caption("Piano Display")
        pygame.display.set_icon(self._load_image("icon")[0])
        # Draws piano
        self.clear()

    def _get_path(self, image_name: str, subdirectory: str = "") -> str:
        """
        Checks if file with name exists at directory. Returns path to file.
        """
        # Builds directory from subdirectory
        directory = f"assets/{subdirectory}"
        # Appends filetype to image name
        image_file = f"{image_name}.png"
        # If image is in directory
        if image_file in os.listdir(directory):
            # Returns a built image path
            return f"{directory}{image_file}"
        else:
            # Raises error
            raise ValueError(f"Image {image_file} not found in {directory}.")

    def _load_image(
        self,
        image_name: str,
        subdirectory: str = "",
        position: tuple[int, int] = (0, 0),
        render: bool = False,
    ) -> tuple[pygame.surface.Surface, pygame.Rect]:
        """
        Pre-loads image at position. Returns pygame surface and rectangle.
        """
        # Creates a path for the image
        image_path = self._get_path(image_name, subdirectory)
        # Creates an alpha surface from the image
        surface = pygame.image.load(image_path).convert_alpha()
        # Creates a rectanlge at position
        rectangle = pygame.Rect(position, surface.get_size())

        # If rendering is set:
        if render:
            # Draws surface in location of rectangle
            self.window.blit(surface, rectangle)
            # Updates display at rectangle
            pygame.display.update(rectangle)

        # Returns surface and rectangle
        return (surface, rectangle)

    def clear(self) -> None:
        """
        Draws piano on display screen.
        """
        # Fills screen with black
        self.window.fill((255, 255, 255))
        # Acquires surface and rectangle from image
        surface, rectangle = self._load_image("piano")
        # For the number of octaves defined:
        for i in range(NUM_OCTAVES):
            # Draws the piano in distributed locations of rectangle on screen
            self.window.blit(surface, rectangle.move(rectangle.width * i, 0))

        # Updates the full display
        pygame.display.flip()

    def update_display(self, keypress: Keypress) -> None:
        """
        Updates keyboard to match keys.
        """
        # Acquires surface and rectangle from image and position
        self._load_image(
            # Image name
            image_name=keypress.letter,
            # Full overlay path
            subdirectory=f"overlays/{keypress.action.name.lower()}/",
            # Position
            position=(
                # X offset
                (keypress.octave - STARTING_OCTAVE) * self.piano_width,
                # Y offset
                0,
            ),
            # Render option
            render=True,
        )


if __name__ == "__main__":

    pygame.init()

    display = Display()

    run = True
    while run:

        pygame.time.Clock().tick(60)

        display.clear()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

    pygame.quit()
