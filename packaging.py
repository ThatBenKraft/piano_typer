from dataclasses import dataclass
from enum import Enum, auto


class Action(Enum):
    """
    Names action types.
    """

    PRESS = auto()
    RELEASE = auto()
    STATIC = auto()


@dataclass
class Keypress:
    """
    Allows for storage of keypress information.
    """

    letter: str = ""
    octave: int = 0
    velocity: int = 0
    timestamp: int = 0
    note: str = ""
    action: Action = Action.STATIC

    def __post_init__(self) -> None:
        """
        Creates a concatenated 'Note' if not already given.
        """
        if self.note == "":
            self.note = f"{self.letter}{self.octave}"
        # Bases action on velocity
        if self.velocity == 64:
            self.action = Action.RELEASE
        elif self.velocity != 0:
            self.action = Action.PRESS

    def is_empty(self) -> bool:
        """
        Returns True if empty.
        """
        return self.action == Action.STATIC

    def to_string(self) -> str:
        """
        Returns current package as a string.
        """
        # Returns empty package representation
        if self.is_empty():
            return f"[ EMPTY PACKAGE ]"
        # Returns populated package representation
        else:
            return (
                f"[ Note: {self.note.center(15)}"
                f"Action: {self.action.name.center(15)}"
                f"Time: {str(self.timestamp).center(15)} ]"
            )
