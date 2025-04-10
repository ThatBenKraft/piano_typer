"""
### Packaging
Supports the storing and manipulation of keystroke events.
"""

__author__ = "Ben Kraft"
__copyright__ = "None"
__credits__ = "Ben Kraft"
__license__ = "Apache"
__version__ = "0.3.0"
__maintainer__ = "Ben Kraft"
__email__ = "ben.kraft@rcn.com"
__status__ = "Prototype"


class Keystroke:
    """
    A class to store and manage keystroke information for musical notes.

    Attributes:
        note: The musical note (e.g., 'A', 'C#').
        octave: The absolute octave for the note.
        is_press: Whether the key is pressed (True) or released (False).
        _full_note: A string combining the note and the octave.
        ACTIONS: The available actions.
        NOTES: The available musical notes ('C' through 'B').
    """

    # Defines action and note constants
    ACTIONS = ("release", "press")
    NOTES = ("C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B")

    def __init__(self, note: str, octave: int, is_press: bool = True) -> None:
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
        self.is_press = is_press
        self._full_note = self.note + str(self.octave)

    def __str__(self) -> str:
        return self._full_note

    def __repr__(self) -> str:
        return str(self)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, (Keystroke, str)):
            return str(self) == str(other)
        return False

    def __hash__(self) -> int:
        return hash(str(self))

    def details(self) -> str:
        """
        Returns note and action details about keypress.
        """
        note_string = f"Note:  {self._full_note}"
        action_string = f"Action:  {'PRESS' if self.is_press else 'RELEASE'}"
        return f"[ {note_string} | {action_string} ]"

    def inverted(self):
        """
        Returns a new instance of Keystroke with the press action inverted.
        """
        return Keystroke(self.note, self.octave, not self.is_press)


if __name__ == "__main__":
    a = Keystroke("A", 0, False)
    d = Keystroke("D#", 0, True)

    print([a, d])
