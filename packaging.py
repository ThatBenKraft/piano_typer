NOTES = ("C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B")


class Keypress:
    """
    Allows for storage of keypress information.
    """

    def __init__(self, note_index: int, octave: int, press: bool = True) -> None:

        if note_index not in range(len(NOTES)):
            raise ValueError(
                f"Invalid note index: {note_index}, number of notes: {len(NOTES)}"
            )

        self.note = NOTES[note_index]
        self.note_index = note_index
        self.octave = octave
        self.full_note = f"{self.note}{self.octave}"
        self.press = press

    def __str__(self) -> str:
        """
        Returns current package as a string.
        """
        # Returns populated package representation
        note_string = f"Note:  {self.full_note}".center(20)
        action_string = f"Action:  {'PRESS' if self.press else 'RELEASE'}".center(20)
        return f"[ {note_string} | {action_string} ]".center(60)

    def inverted(self):
        """
        Returns instance of Keypress with inverted action.
        """
        self.press = not self.press
        return self


if __name__ == "__main__":
    print(Keypress(10, 0, False))
    print(Keypress(0, 0, True))
