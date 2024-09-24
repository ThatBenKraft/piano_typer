NOTES = ("C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B")


class Keystroke:
    """
    Allows for storage of keystroke information.
    """

    def __init__(self, note: str, octave: int, press: bool = True) -> None:
        """
        Allows for storage of keystroke information.
        """
        self.note = note.upper()
        if self.note not in NOTES:
            raise ValueError(f"Invalid note: {self.note}, available notes: {NOTES}")
        self.octave = octave
        self.press = press
        self.full_note = f"{self.note}{self.octave}"

    def __str__(self) -> str:
        return self.full_note

    def __repr__(self) -> str:
        """
        Returns current package as a string.
        """
        # Returns populated package representation
        note_string = f"Note:  {self.full_note}".center(20)
        action_string = f"Action:  {'PRESS' if self.press else 'RELEASE'}".center(20)
        return f"[ {note_string} | {action_string} ]".center(60)

    def __eq__(self, other: object) -> bool:

        if isinstance(other, Keystroke):
            return self.full_note == other.full_note
        return False

    def __hash__(self) -> int:
        return hash(self.full_note)

    def inverted(self):
        """
        Returns instance of Keystroke with inverted action.
        """
        self.press = not self.press
        return self


if __name__ == "__main__":
    print(Keystroke("A", 0, False))
    print(Keystroke("D#", 0, True))
