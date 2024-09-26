"""
### Packaging
Supports the storing and manipulation of keystroke events.
"""

__author__ = "Ben Kraft"
__copyright__ = "None"
__credits__ = "Ben Kraft"
__license__ = "Apache"
__version__ = "0.1.2"
__maintainer__ = "Ben Kraft"
__email__ = "ben.kraft@rcn.com"
__status__ = "Prototype"


class Keystroke:
    """
    A class to store and manage keystroke information for musical notes.

    Attributes:
        note: The musical note (e.g., 'A', 'C#').
        octave: The absolute octave for the note.
        press: Whether the key is pressed (True) or released (False).
        full_note: A string combining the note and the octave.
        ACTIONS: The available actions.
        NOTES: The available musical notes ('C' through 'B').
    """

    # Defines action and note constants
    ACTIONS = ("release", "press")
    NOTES = ("C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B")

    def __init__(self, note: str, octave: int, press: bool = True) -> None:
        """
        Initializes a Keystroke object with note, octave, and press status.

        Args:
            note: The musical note (e.g., 'A', 'C#').
            octave: The absolute octave for the note.
            press: Whether the key is pressed (True) or released (False).

        Raises:
            ValueError: If the note is not a valid musical note.
        """
        self.note = note.upper()
        if self.note not in self.NOTES:
            raise ValueError(
                f"Invalid note: {self.note}, available notes: {self.NOTES}"
            )
        if octave < 0:
            raise ValueError(f"Invalid octave: {self.octave}")
        self.octave = octave
        self.press = press
        self.full_note = self.note + str(self.octave)

    def __str__(self) -> str:
        return self.full_note

    def __repr__(self) -> str:
        """
        Returns current keystroke as a string representation.
        """
        note_string = f"Note:  {self.full_note}".center(20)
        action_string = f"Action:  {'PRESS' if self.press else 'RELEASE'}".center(20)
        return f"[ {note_string} | {action_string} ]".center(60)

    def __eq__(self, other: object) -> bool:
        """
        Compares two Keystroke objects for equality, based on the full_note.
        """
        if isinstance(other, Keystroke):
            return self.full_note == other.full_note
        return False

    def __hash__(self) -> int:
        """
        Returns the hash of the Keystroke, based on the full_note.
        """
        return hash(self.full_note)

    def inverted(self):
        """
        Returns a new instance of Keystroke with the action inverted (pressed/released).
        """
        return Keystroke(self.note, self.octave, not self.press)


if __name__ == "__main__":
    print(Keystroke("A", 0, False))
    print(Keystroke("D#", 0, True))
