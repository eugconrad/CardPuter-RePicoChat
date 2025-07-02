import asyncio
import neopixel
import time
from machine import Pin
from micropython import const

from lib.hydra import beeper

from .picochat import Client
from .utils import Config, Display, UserInput, WiFi, TextInput

AFK_DELAY = const(10)
UPDATE_DELAY = const(5)


class App:
    def __init__(self):
        # sd = sdcard.SDCard()
        # sd.mount()

        self.config = Config()
        self.display = Display()
        self.beep = beeper.Beeper()
        self.kb = UserInput()

        self.wifi = WiFi()
        self.wifi.callback = self.display.alert

        self.client = Client(self.config)
        self.client.on_request_start = self.on_request_start
        self.client.on_request_end = self.on_request_end
        self.client.on_update = self.on_update
        self.client.on_new_message = self.on_new_message

        self.text_input = TextInput(self.config.palette[4], self.config.palette[8])

        self.is_afk = False
        self.afk_timer = self.set_timeout(AFK_DELAY)
        self.update_timer = self.set_timeout(UPDATE_DELAY)

        self.led = neopixel.NeoPixel(Pin(21), 1, bpp=3)

        self._ti_rect_h = 16
        self._ti_text_h = self.display.height - self._ti_rect_h + 4
        self._bg_rect_h = self.display.height - self._ti_rect_h
        self._max_lines = (self.display.height - self._ti_rect_h - 4) // 8
        self._max_line_chars = (self.display.width - 8) // 8

    def on_request_start(self):
        self.led.fill((50, 25, 0))
        self.led.write()

    def on_request_end(self):
        self.led.fill((0, 0, 0))
        self.led.write()

    @staticmethod
    def set_timeout(sec=5):
        return time.ticks_add(time.ticks_ms(), sec*1000)

    def handle_keys(self, keys):
        for key in keys:
            if key == "UP":
                self.text_input.end_cursor()
            elif key == "DOWN":
                self.text_input.reset_cursor()
            elif key == "LEFT":
                self.text_input.move_cursor(-1)
            elif key == "RIGHT":
                self.text_input.move_cursor(1)
            elif key == "BSPC":
                self.text_input.del_char(-1)
            elif key == "DEL":
                self.text_input.del_char(1)
            elif key == "SPC":
                self.text_input.add_char(" ")
            elif len(key) == 1:
                self.text_input.add_char(key)

            elif key == "ENT":
                self.client.update(self.client.send_message(self.text_input.get_text()))
                self.text_input.clear()

    @staticmethod
    def _wrap_text(text, width):
        words = str(text).split(' ')
        lines = []
        line = ""
        for w in words:
            if len(line) + len(w) + 1 <= width:
                line += w + " "
            else:
                lines.append(line.rstrip())
                line = w + " "
        if line:
            lines.append(line.rstrip())
        return lines

    def on_update(self, messages):
        self.draw_message_box(messages)

    def on_new_message(self):
        self.beep.play("C4", 50)

    def draw_message_box(self, messages):
        self.display.fill_rect(0, 0, self.display.width, self._bg_rect_h, self.config.palette[2])
        lines = []
        for msg in messages:
            lines.extend(self._wrap_text(msg, self._max_line_chars))
        start_y = self._bg_rect_h - 8 * len(lines[-self._max_lines:])
        for i, line in enumerate(lines[-self._max_lines:]):
            self.display.text(line, 4, start_y + i * 8, self.config.palette[8])

    def draw_text_input(self):
        # Text input rect
        self.display.fill_rect(
            0, self._bg_rect_h, self.display.width, self._ti_rect_h,
            self.config.palette[3] if self.is_afk else self.config.palette[4]
        )
        # Text input
        self.display.text(
            self.text_input.get_visible_text(), 4, self._ti_text_h,
            self.config.palette[7] if self.is_afk else self.config.palette[8]
        )
        # Cursor
        if not self.is_afk:
            self.display.text("|", self.text_input.cursor_x + 4, self._ti_text_h, self.text_input.tick())

    async def run(self):
        self.wifi.connect(self.config["wifi_ssid"], self.config["wifi_pass"])

        self.display.alert(f"Welcome, {self.config.username}!")
        await asyncio.sleep(1)

        try:
            self.client.update(self.client.get_messages())
        except Exception as e:
            self.display.alert(f"Error: {e}")
            await asyncio.sleep(5)

        self.afk_timer = self.set_timeout(AFK_DELAY)

        while True:
            keys = self.kb.get_new_keys()

            if keys:
                self.handle_keys(keys)
                self.is_afk = False
                self.afk_timer = self.set_timeout(AFK_DELAY)

            if not self.is_afk:
                if time.ticks_diff(time.ticks_ms(), self.afk_timer) > 0:
                    self.is_afk = True
                self.draw_text_input()

            self.display.show()

            if self.is_afk:
                if time.ticks_diff(time.ticks_ms(), self.update_timer) > 0:
                    self.client.update(self.client.get_messages())
                    self.update_timer = self.set_timeout(UPDATE_DELAY)

            await asyncio.sleep(0)


asyncio.run(App().run())
