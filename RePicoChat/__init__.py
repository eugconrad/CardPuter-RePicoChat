import asyncio

from lib.hydra.popup import UIOverlay

from .app import App
from .client import PicoChatConfig, PicoChatClient
from .textinput import Cursor, TextInputManager


async def main():
    app = App(app_name="RePicoChat", enable_wlan=True)

    config = PicoChatConfig(hydra_config=app.config)
    client = PicoChatClient(pico_chat_config=config)

    cursor = Cursor(app.display.FG_COLOR, app.display.TEXT_COLOR)
    text_input = TextInputManager(cursor=cursor)

    app.display.alert(f"Welcome, {config.username}!")

    def options():
        ov = UIOverlay()
        while True:
            app.display.clear()
            choice = ov.popup_options(
                options=[
                    ["Change username", "Change server", "Quit", "Back"],
                ],
                title="Settings"
            )
            if choice == "Change username":
                while True:
                    name = ov.text_entry(config.username, "Enter username:").strip()
                    if 3 <= len(name) <= 16:
                        config.username = name
                        ov.popup(f"Username changed to: {name}")
                        break
                    ov.error("Username must be 3–16 characters long.")
            elif choice == "Change server":
                while True:
                    srv = ov.popup_options(
                        options=[[
                            "picochat-server.fly.dev",
                            "picochat-server.eugconrad.com",
                            "Custom server"
                        ]],
                        title="Settings"
                    )
                    srv = ov.text_entry(config.server, "Enter server:").strip() if srv == "Custom server" else srv
                    if srv and "." in srv and " " not in srv:
                        config.server = srv
                        ov.popup(f"Server changed to: {srv}")
                        break
                    ov.error("Invalid address.")
            elif choice == "Quit":
                app.quit()
            elif choice == "Back":
                break

    def on_new_messages(msgs):
        app.display.display.fill_rect(0, 0, app.display.DISPLAY_WIDTH, 120, app.display.BG_COLOR)
        lines = []
        for m in msgs[-15:]:
            lines += client.wrap_text(m)
        for i, line in enumerate(lines[-15:]):
            app.display.display.text(line, 4, 8 * i + 4, app.display.TEXT_COLOR)
        app.display.display.show()

    client.on_new_messages = on_new_messages

    try:
        client.update()
    except Exception as e:
        app.display.alert(f"Error: {e}")

    while True:
        keys = app.userinput.get_new_keys()
        if keys:
            for key in keys:
                if key == "UP":
                    text_input.cursor.to_end(len(text_input.input_chars))
                elif key == "DOWN":
                    text_input.cursor.to_start()
                elif key == "LEFT":
                    text_input.cursor.move(-1, len(text_input.input_chars))
                elif key == "RIGHT":
                    text_input.cursor.move(1, len(text_input.input_chars))
                elif key == "BSPC":
                    text_input.del_char(-1)
                elif key == "DEL":
                    text_input.del_char(1)
                elif key == "SPC":
                    text_input.add_char(" ")
                elif key == "ESC":
                    app.quit()
                elif key == "G0":
                    options()
                    client.update(get=False)
                elif len(key) == 1:
                    text_input.add_char(key)
                elif key == "ENT":
                    client.send_message(text_input.get_text())
                    text_input.clear()
                    client.update()

        app.display.display.fill_rect(
            0, 120, app.display.DISPLAY_WIDTH, app.display.DISPLAY_HEIGHT, app.display.FG_COLOR
        )

        app.display.display.text(
            text_input.get_visible_text(),
            4, 124, app.display.TEXT_COLOR
        )

        cursor_color = text_input.cursor.tick()
        app.display.display.text(
            "|",
            text_input.cursor.x + 4, 124, cursor_color
        )

        app.display.display.show()

        await asyncio.sleep(0)


asyncio.run(main())
