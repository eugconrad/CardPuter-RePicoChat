# CardPuter-RePicoChat
A [PicoChat](https://github.com/PixelDud/PicoChat-Server) client for the M5Stack CardPuter, written in MicroPython for use with [MicroHydra](https://github.com/echo-lalia/Cardputer-MicroHydra).

A redesigned PicoChat client for M5Stack Cardputer, written in MicroPython for use with MicroHydra. This version features improved UI, real-time message updates, and in-app configuration.

## Features
- Real-time chat interface with message history
- In-app settings configuration (no manual file editing required)
- Customizable username (3-16 characters)
- Configurable server URL
- Keyboard-driven interface with intuitive controls
- Message wrapping for long text

## Installation
1. Place the `RePicoChat` folder into the `apps/` directory on your MicroHydra SD card
2. Insert the SD card into your Cardputer
3. Launch from the MicroHydra app menu

## Chat Interface
- Type your message using the keyboard
- Messages automatically wrap when exceeding display width
- Press `Enter` to send your message
- The display shows the last 15 messages in the chat

## Controls
| Key       | Action                  |
|-----------|-------------------------|
| Enter     | Send message or update  |
| ESC       | Quit app                |
| G0        | Settings menu           |
| Backspace | Delete previous char    |
| Delete    | Delete next char        |
| Arrow Keys| Move cursor             |
| Up/Down   | Jump to start/end       |

## Settings menu (press G0)
- **Change Username**: Set 3-16 char name
- **Change Server**: Configure server URL
- **Back**: Return to chat

## Default Config
- Username: `user` (prompted to change)
- Server: `picochat.micronova.dev`

## Requirements
- M5Stack Cardputer
- MicroHydra 2.4+ firmware
- WiFi connection

## Troubleshooting
1. Verify WiFi connection
2. Check server URL
3. Ensure server is online

Error messages appear as popups.

<hr>

`base64.py` is sourced from [here](https://github.com/micropython/micropython-lib/blob/master/python-stdlib/base64/base64.py) and licensed under [this](https://www.python.org/download/releases/3.3.5/license/) license.
