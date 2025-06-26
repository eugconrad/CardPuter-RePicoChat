import asyncio
import neopixel
import time
from machine import Pin

from lib.hydra.popup import UIOverlay

from .app import App
from .client import PicoChatConfig, PicoChatClient
from .textinput import Cursor, TextInputManager


class Core:

    def __init__(self):
        self.app = App(app_name="RePicoChat", enable_wlan=True)
        self.config = PicoChatConfig(hydra_config=self.app.config)
        self.client = PicoChatClient(pico_chat_config=self.config)

        self.cursor = Cursor(self.app.display.FG_COLOR, self.app.display.TEXT_COLOR)
        self.text_input = TextInputManager(cursor=self.cursor)

        self._strip = neopixel.NeoPixel(Pin(21), 1, bpp=3)

        self.client.callback = self.on_new_messages
        self.client.on_request_start = self.on_request_start
        self.client.on_request_end = self.on_request_end
        self.afk = False
        self.update_timer = time.ticks_ms()
        self.running = True

    def on_request_start(self):
        self._strip.fill((50, 25, 0))
        self._strip.write()

    def on_request_end(self):
        self._strip.fill((0, 0, 0))
        self._strip.write()

    def reset_update_timer(self):
        self.update_timer = time.ticks_ms()

    async def run(self):
        self.app.display.alert(f"Welcome, {self.config.username}!")

        try:
            self.client.update()
        except Exception as e:
            self.app.display.alert(f"Error: {e}")

        while self.running:
            keys = self.app.userinput.get_new_keys()
            if keys:
                await self.handle_keys(keys)
                self.afk = False
                self.reset_update_timer()

            self.draw_input()

            now = time.ticks_ms()
            if time.ticks_diff(now, time.ticks_add(self.update_timer, 5000 if self.afk else 10000)) > 0:
                self.client.update()
                self.afk = True
                self.reset_update_timer()

            await asyncio.sleep(0)

    async def handle_keys(self, keys):
        for key in keys:
            if key == "UP":
                self.text_input.cursor.to_end(len(self.text_input.input_chars))
            elif key == "DOWN":
                self.text_input.cursor.to_start()
            elif key == "LEFT":
                self.text_input.cursor.move(-1, len(self.text_input.input_chars))
            elif key == "RIGHT":
                self.text_input.cursor.move(1, len(self.text_input.input_chars))
            elif key == "BSPC":
                self.text_input.del_char(-1)
            elif key == "DEL":
                self.text_input.del_char(1)
            elif key == "SPC":
                self.text_input.add_char(" ")
            elif len(key) == 1:
                self.text_input.add_char(key)

            elif key == "ESC":
                self.app.quit()
                self.running = False
            elif key == "G0":
                self.show_options()
                self.client.update(get=False)
            elif key == "ENT":
                text = self.text_input.get_text()
                (self.text_input.clear(), self.client.send_message(text), self.client.update(get=not text))

    def draw_input(self):
        d = self.app.display.display
        d.fill_rect(
            0, 120, self.app.display.DISPLAY_WIDTH, self.app.display.DISPLAY_HEIGHT,
            self.app.display.FG_COLOR_DARK if self.afk else self.app.display.FG_COLOR
        )
        d.text(
            self.text_input.get_visible_text(), 4, 124,
            self.app.display.TEXT_COLOR_DARK if self.afk else self.app.display.TEXT_COLOR
        )
        if not self.afk:
            d.text("|", self.text_input.cursor.x + 4, 124, self.text_input.cursor.tick())
        d.show()

    def on_new_messages(self, msgs):
        d = self.app.display.display
        d.fill_rect(0, 0, self.app.display.DISPLAY_WIDTH, 120, self.app.display.BG_COLOR)
        lines = []
        for m in msgs[-15:]:
            lines += self.client.wrap_text(m)
        for i, line in enumerate(lines[-15:]):
            d.text(line, 4, 8 * i + 4, self.app.display.TEXT_COLOR)
        d.show()

    def show_options(self):
        ov = UIOverlay()
        while True:
            self.app.display.clear()
            choice = ov.popup_options(
                options=[["Change username", "Change server", "Quit", "Back"]],
                title="Settings"
            )
            if choice == "Change username":
                while True:
                    name = ov.text_entry(self.config.username, "Enter username:").strip()
                    if 3 <= len(name) <= 16:
                        self.config.username = name
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
                    srv = ov.text_entry(self.config.server, "Enter server:").strip() if srv == "Custom server" else srv
                    if srv and "." in srv and " " not in srv:
                        self.config.server = srv
                        ov.popup(f"Server changed to: {srv}")
                        break
                    ov.error("Invalid address.")
            elif choice == "Quit":
                self.app.quit()
                self.running = False
                break
            elif choice == "Back":
                break


asyncio.run(Core().run())
