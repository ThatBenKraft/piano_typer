# Piano Typer 🎹💻🎶

This project allows you to use your piano as you would your keyboard and mouse, with a fancy digital display to boot.

Python dependencies: **`pygame`**, **`PIL`**, **`keyboard`**, **`mouse`**

## 📔 Modules

### 📦 `packaging.py`

The `Keystroke` class allows for easy storage of midi events, whether pressing or releasing a key. Stores a note, octave, and press state. The state (`False` for "release" or `True` for "press") can be flipped with `Keystroke.inverted()`

Equality and hashing is dependent solely on an object's `full_note` member, which is a string combination of the note and octave (eg. "C#4")

The default members `Keystroke.ACTIONS` and `Keystroke.NOTES` contain all available actions and notes, respectively.

### 🎹 `midi.py`

The `midi` module supplies helpful methods in setting up and querying MIDI devices:

- **`midi.get_device()`** - Initializes and lists USB MIDI devices. Returns first found input device.
- **`midi.get_device_info()`** - Accesses specified device information. Returns tuple of name and state.
- **`midi.parse_event()`** - Parses midi event into keystroke.
- **`midi.get_keystrokes()`** - Reads a specified number of MIDI events from the device. Returns any corresponding keystrokes.

### 🖥️ `visuals.py`

The `Display` class allows for `Keystoke`s to be represented visually as key presses on a piano, creating a window that can be updated live.

- **`Display.update_key()`** - Updates display with specified keypress.
- **`Display.refresh()`** - Redraws all elements on-screen, including any key presses held in memory that have not been "released".
- **`Display.tick()`** - Can be used in a loop to limit the display's frame rate.
- **`Display.is_closed()`** - Detects if window has been manually closed
- **`Display.close()`** - Closes window.

### 🚀 `main.py`

The `Program` class runs all actions for the Piano Typer. It can be run with `Program.run()` and closed with `Program.close()`.

`Keybinds` contains all associations from full notes to computer keys, sorted by type (keyboard, mouse, cursor, etc.). All keybinds can be set in `keybinds.json`.

## 🔣 Supplementary

### 📤 `piano_export.py`

A small module used to manipulate, animate, and export frames from a `Display` as .png's, .gif's, etc.

### 🖨️ `assets/export.jsx`

A small JavaScript module used to programmatically export assets from `assets/keyboard.ai`.

### 🖌️ `assets/` Collection

- **`assets/keyboard.ai`** - Contains vector art for keys and icon.
- **`assets/octave.png`** - Acts as a base image for the piano display.
- **`assets/icon.png`** - Acts as an icon for the display window.
