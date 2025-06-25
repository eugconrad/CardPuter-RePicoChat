import asyncio

from lib.hydra import popup

from .app import App
from .client import PicoChatConfig, PicoChatClient
from .textinput import TextInputManager


async def main():
    """
    Initialize and run the RePicoChat application.

    This asynchronous function sets up the application with WLAN connectivity,
    configures the chat client, and manages user input for sending messages.
    It also provides options for changing the username and server settings
    through a UI overlay. The function continuously listens for keyboard input
    to handle message editing and sending, as well as cursor movement.

    Attributes:
        app (App): The main application instance.
        config (PicoChatConfig): Configuration for the chat client.
        client (PicoChatClient): The chat client instance.
        text_input (TextInputManager): Manages text input and cursor behavior.

    Functions:
        options(): Handles the settings menu for changing username and server.
        on_new_messages(messages: list): Updates the display with new messages.

    Keyboard Controls:
        - Arrow keys: Move the cursor.
        - BSPC/DEL: Delete characters.
        - SPC: Add a space.
        - ENT: Send the message.
        - ESC: Quit the application.
        - G0: Open settings menu.
    """
    app = App(app_name="RePicoChat", enable_wlan=True)

    config = PicoChatConfig(hydra_config=app.config)
    client = PicoChatClient(pico_chat_config=config)
    text_input = TextInputManager()

    app.display.alert(text=f"Welcome, {config.username}!")

    def options():
        overlay = popup.UIOverlay()
        while True:
            app.display.clear()

            # главное меню настроек
            choice = overlay.popup_options(
                options=[[
                    "Change username",
                    "Change server",
                    "Back"
                ]],
                title="Settings"
            )

            if choice == "Change username":
                while True:
                    new_username = overlay.text_entry(
                        start_value=config.username,
                        title="Enter username:"
                    ).strip()

                    if 3 <= len(new_username) <= 16:
                        config.username = new_username
                        overlay.popup(f"Username changed to: {new_username}")
                        break
                    else:
                        overlay.error("Username must be 3–16 characters long.")

            elif choice == "Change server":
                while True:
                    new_server = overlay.text_entry(
                        start_value=config.server,
                        title="Enter server URL:"
                    ).strip()

                    if new_server and "." in new_server and " " not in new_server:
                        config.server = new_server
                        overlay.popup(f"Server changed to: {new_server}")
                        break
                    else:
                        overlay.error("Invalid server address.")

            elif choice == "Back":
                break

    def on_new_messages(messages: list):
        app.display.display.fill_rect(
            0, 0,
            app.display.DISPLAY_WIDTH, 120,
            app.display.BG_COLOR
        )
        wrapped_lines = []
        for msg in messages[-15:]:
            lines = client.wrap_text(msg)
            wrapped_lines.extend(lines)
        wrapped_lines = wrapped_lines[-15:]
        for i, line in enumerate(wrapped_lines):
            y = 8 * i + 4
            app.display.display.text(
                line,
                4, y,
                app.display.TEXT_COLOR
            )
        app.display.display.show()

    client.on_new_messages = on_new_messages
    # asyncio.create_task(client.start_polling())

    try:
        client.update()
    except Exception as err:
        app.display.alert(f"Error: {err}")

    while True:
        # Keyboard handling
        keys = app.userinput.get_new_keys()

        if keys:
            for key in keys:

                # Handle cursor movement
                if key == "UP":
                    text_input.cursor.to_end()
                elif key == "DOWN":
                    text_input.cursor.to_start()
                elif key == "LEFT":
                    text_input.cursor.move(direction=-1)
                elif key == "RIGHT":
                    text_input.cursor.move(direction=1)

                # Handle message editing
                elif key == "BSPC":
                    text_input.del_char(direction=-1)
                elif key == "DEL":
                    text_input.del_char(direction=1)
                elif key == "SPC":
                    text_input.add_char(char=" ")

                elif key == "ESC":
                    app.quit()
                elif key == "G0":
                    options()
                    client.update(get_messages=False)

                elif len(key) == 1:
                    text_input.add_char(char=key)

                # Send message only when Enter is pressed
                elif key == "ENT":
                    client.send_message(message=text_input.input_text)
                    text_input.clear()
                    client.update()

        # Displays message being edited
        app.display.display.fill_rect(
            0, 120,
            app.display.DISPLAY_WIDTH, app.display.DISPLAY_HEIGHT,
            app.display.BG_COLOR_DARK
        )
        app.display.display.text(
            text_input.get_visible_text(),
            app.display.CHAR_WIDTH, 124,
            app.display.TEXT_SHADOW_COLOR
        )
        if text_input.cursor.tick():
            app.display.display.text(
                "|",
                text_input.cursor.x, 124,
                app.display.TEXT_COLOR
            )
        app.display.display.show()

        await asyncio.sleep(0)


asyncio.run(main())
