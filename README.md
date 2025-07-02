# CardPuter-RePicoChat
A [PicoChat](https://github.com/PixelDud/PicoChat-Server) client for the M5Stack CardPuter, written in MicroPython for use with [MicroHydra](https://github.com/echo-lalia/Cardputer-MicroHydra).

A redesigned PicoChat client for M5Stack Cardputer featuring improved UI, real-time message updates, and in-app configuration.

## Features
- Real-time chat interface with message history (last 15 messages)
- Smart AFK mode:
  - Activates after 10 seconds of inactivity
  - Dims input UI
  - Increases message update frequency to every 5 seconds
- In-app settings configuration (no manual file editing required)
- Customizable username (3-16 characters)
- Multiple server presets + custom server option
- Keyboard-driven interface with intuitive controls
- Message wrapping for long text
- Visual feedback during network requests (NeoPixel indicator)
- Asynchronous operation for smooth performance

## Installation
1. Place the `RePicoChat` folder into the `apps/` directory on your MicroHydra SD card
2. Insert the SD card into your Cardputer
3. Launch from the MicroHydra app menu

## Chat Interface
- Type your message using the keyboard
- Messages automatically wrap when exceeding display width
- Press `Enter` to send your message
- Interface dims after 10 seconds of inactivity (AFK mode)
  - In AFK mode, messages update every 5 seconds (instead of 10s in active mode)
  - Any keypress returns to normal active mode
- NeoPixel lights up orange during network activity

## Activity Monitoring
| Mode      | Activation Time | Update Frequency | UI Appearance  |
|-----------|-----------------|------------------|----------------|
| Active    | During typing   | Every 10 seconds | Bright         |
| AFK       | 10s inactivity  | Every 5 seconds  | Dimmed         |

## Controls
| Key       | Action                  |
|-----------|-------------------------|
| Enter     | Send message            |
| ESC       | Quit app                |
| G0        | Open settings menu      |
| Backspace | Delete previous char    |
| Delete    | Delete next char        |
| Arrow Keys| Move cursor             |
| Up        | Jump to end of input    |
| Down      | Jump to start of input  |
| Space     | Insert space            |
| Any key   | Exit AFK mode           |

## Settings Menu (press G0)
- **Change Username**: Set 3-16 character name
- **Change Server**: Choose from presets or enter custom URL
  - picochat-server.fly.dev
  - picochat-server.eugconrad.com
  - Custom server option
- **Quit**: Exit application
- **Back**: Return to chat

## Technical Details
- Uses MicroPython's asyncio for asynchronous operation
- Built on MicroHydra's UI framework
- Includes visual feedback systems:
  - NeoPixel indicator for network activity
  - UI dimming in AFK mode
  - Cursor blink animation
- Automatic message updates every 10s (5s in AFK mode)

## Default Config
- Username: `user` (prompted to change on first run)
- Server: `picochat.micronova.dev`

## Requirements
- M5Stack Cardputer
- MicroHydra 2.4+ firmware
- WiFi connection

## Troubleshooting
1. Verify WiFi connection
2. Check server URL in settings
3. Ensure server is online
4. Check NeoPixel for network activity indication

Error messages appear as popups.

<hr>

`base64.py` is sourced from [here](https://github.com/micropython/micropython-lib/blob/master/python-stdlib/base64/base64.py) and licensed under [this](https://www.python.org/download/releases/3.3.5/license/) license.
