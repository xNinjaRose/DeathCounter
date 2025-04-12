# Death Counter

A customizable desktop application for tracking deaths or events, perfect for streamers, speedrunners, or anyone needing a visual counter. Features a graphical interface, hotkey support, sound effects, and a history log, with options for themes, colors, and green screen mode for streaming.


## Features

- **Track Deaths or Events**: Increment, decrement, or reset a counter with a click or hotkey.
- **Customizable Display**: Change the counter name and text colors (hex codes).
- **Hotkey Support**: Bind keyboard keys or mouse buttons (e.g., `+`, `-`, `mouse4`) to control the counter.
- **Green Screen Mode**: Hide buttons for a clean overlay in streaming software like OBS.
- **Sound Effects**: Plays a "ding" sound on increment (using the included `ding.mp3`).
- **History Log**: View a timestamped record of all counter actions.
- **Themes**: Toggle between light and dark modes.
- **Persistent Data**: Saves settings and counter state to a local database.
- **Pause Mode**: Temporarily disable hotkeys to prevent accidental inputs.

## Installation

### Prerequisites

- **Windows** (tested on Windows 10/11; may work on macOS/Linux with compatibility layers like Wine).
- A modern mouse/keyboard for hotkey bindings.

### Steps

1. **Download the ZIP**:
   - Download the `death-counter.zip` file from the [Releases](https://github.com/xNinjaRose/DeathCounter/releases) page on GitHub.
   - Extract the ZIP file to a folder on your computer (e.g., `C:\Neko Death Counter v 3_0_0`).

2. **Verify Contents**:
   - Ensure the extracted folder contains:
     - `Neko Death Counter v 3_0_0.exe`: The main executable file.
     - `ding.mp3`: The sound file for increment events.
     - (Optional) Other dependency files required by the executable.

3. **Run the App**:
   - Double-click `Neko Death Counter v 3_0_0.exe` to launch the application.
   - **Note**: If you encounter a Windows SmartScreen warning, click "More info" and then "Run anyway" to allow the app to run. If hotkeys don’t work, try running as administrator (right-click `Neko Death Counter v 3_0_0.exe` > Run as Administrator).

## Usage

1. **Launch the App**:
   - Double-click `Neko Death Counter v 3_0_0.exe`. A window opens with the counter (default name: "Deaths").

2. **Control the Counter**:
   - **Buttons**: Click `+` to increment, `-` to decrement, or `Reset` to zero the counter.
   - **Hotkeys**: Press the default hotkeys (`+` for increment, `-` for decrement) or set custom ones.
   - **Mouse Buttons**: Supports extra mouse buttons (e.g., `mouse4`, `mouse5`) for MMO mice.

3. **Customize**:
   - **Change Name**: Click "Change Counter Name" to rename (e.g., "Boss Kills").
   - **Set Colors**: Click "Set Text Color" and enter hex codes (e.g., `#FF0000` for red).
   - **Set Hotkeys**: Click "Set Hotkeys" and enter keys like `i`, `ctrl+m`, or `mouse4`. Examples are shown in the dialog.
   - **Toggle Theme**: Click "Toggle Dark Mode" for light/dark themes.
   - **Green Screen**: Click "Green Screen Mode" for a minimal view (great for OBS overlays).
   - **Pause**: Click "Pause Counter" to disable hotkeys temporarily.
   - **View History**: Click "View History" to see all actions with timestamps.

4. **For Streaming**:
   - Use green screen mode and capture the window in OBS with a chroma key filter (green background).
   - Resize/position the counter overlay as needed.

## Troubleshooting

- **Hotkeys Not Working**:
  - Run the app as administrator (right-click `Neko Death Counter v 3_0_0.exe` > Run as Administrator).
  - Avoid conflicting hotkeys (check other apps like Discord).
  - Try simple keys like `i` or `h`, or mouse buttons like `mouse4`.
- **No Sound**:
  - Ensure `ding.mp3` is in the same folder as `Neko Death Counter v 3_0_0`.
  - Check your system audio settings.
- **App Freezes**:
  - Close and restart the app.
  - Ensure no other apps are intercepting hotkeys.
- **App Won’t Start**:
  - Ensure all files from the ZIP are extracted to the same folder.
  - Check if your antivirus is blocking the executable; add an exception if needed.
  - Verify your system meets the requirements (Windows 10/11 recommended).

## File Structure

- `Neko Death Counter v 3_0_0.exe`: Main executable file.
- `ding.mp3`: Sound file for increment events (included in the ZIP).
- `Neko Death Counter v 3_0_0.db`: Auto-generated SQLite database for settings and history (don’t edit manually).

## License

[MIT License](LICENSE) — Free to use, modify, and distribute.

## Contact

For bugs or suggestions, open an issue on GitHub.
