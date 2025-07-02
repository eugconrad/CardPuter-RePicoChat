import network
import random
import requests
import time

from lib import display, userinput
from lib.hydra import config


class WiFi:
    def __init__(self):
        self.callback = None
        self.nic = None

    def connect(self, wifi_ssid, wifi_pass):
        try:
            self.nic = network.WLAN(network.STA_IF)
        except Exception as e:
            if self.callback:
                self.callback(f"WiFi init failed: {e}")
            time.sleep(2)
            return False
        if self.callback:
            self.callback("Turning on WIFI module...")
        self.nic.active(True)

        if not self.nic.isconnected():
            try:
                if self.callback:
                    self.callback(f"Attempting to connect to WIFI network {wifi_ssid}...")
                self.nic.connect(wifi_ssid, wifi_pass)
            except Exception as err:
                if self.callback:
                    self.callback(f"Error during WIFI connection: {err}")
                time.sleep(5)
                return False

        for i in range(1, 6):
            try:
                if self.callback:
                    self.callback("Checking internet connectivity...")
                r = requests.get("http://1.1.1.1/")
                if r.status_code == 200:
                    if self.callback:
                        self.callback("Internet connection established successfully!")
                    return True
            except Exception as err:
                if i > 2:
                    if self.callback:
                        self.callback(f"[{i}] Retrying internet connectivity check: {err}")
                time.sleep(1)
        return False


class Display(display.Display):
    def alert(self, text):
        self.fill(self.palette[2])
        max_chars = self.width // 8
        lines = []
        line = ""
        for word in text.split():
            if len(line) + len(word) + (1 if line else 0) <= max_chars:
                line += (" " if line else "") + word
            else:
                lines.append(line)
                line = word
        if line:
            lines.append(line)
        total_height = len(lines) * 12
        y = (self.height - total_height) // 2

        for line in lines:
            x = (self.width - len(line) * 8) // 2
            self.text(line, x, y, self.palette[8])
            y += 12
        self.show()


class UserInput(userinput.UserInput):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._custom_combinations = []
        self._required_modifiers = []

    def register_combination(self, keys, callback, require_modifiers=None) -> None:
        if require_modifiers is None:
            require_modifiers = []
        self._custom_combinations.append((keys, callback, require_modifiers))

    def system_commands(self, keylist) -> None:
        super().system_commands(keylist)
        for keys, callback, req_modifiers in self._custom_combinations:
            modifiers_ok = all(mod in self.key_state for mod in req_modifiers)
            keys_ok = all(key in keylist for key in keys)
            if modifiers_ok and keys_ok:
                for key in keys:
                    if key in keylist:
                        keylist.remove(key)
                callback()


class Config(config.Config):
    @property
    def server(self):
        key = "pico_chat_server"
        if key not in self.config:
            self.config[key] = "picochat-server.fly.dev"
        return self.config[key]

    @server.setter
    def server(self, value):
        self.config["pico_chat_server"] = str(value)
        self.config.save()

    @property
    def username(self):
        key = "pico_chat_username"
        if key not in self.config:
            self.config[key] = "User_" + str(random.randint(1000, 9999))
        return self.config[key]

    @username.setter
    def username(self, value):
        self.config["pico_chat_username"] = str(value)
        self.config.save()


class TextInput:
    def __init__(self, color_bg, color_fg):
        self.input_chars = []

        self.pos = 0

        self.blink = 500

        self.color_bg = color_bg
        self.color_fg = color_fg

        self.step = 0
        self.steps = 50

        self.height_size = 120

    # курсор
    def move_cursor(self, direction):
        self.pos = max(0, min(self.pos + direction, len(self.input_chars)))

    def reset_cursor(self):
        self.pos = 0

    def end_cursor(self):
        self.pos = min(len(self.input_chars), 28)

    @property
    def cursor_x(self):
        return min(self.pos, 28) * 8

    def tick(self):
        self.step = (self.step + 1) % (self.steps * 2)
        p = self.step if self.step < self.steps else self.steps * 2 - self.step
        bg, fg = self.color_bg, self.color_fg
        return (
                (((bg >> 11) & 0x1F) + (((fg >> 11) & 0x1F) - ((bg >> 11) & 0x1F)) * p // self.steps) << 11 |
                (((bg >> 5) & 0x3F) + (((fg >> 5) & 0x3F) - ((bg >> 5) & 0x3F)) * p // self.steps) << 5 |
                ((bg & 0x1F) + ((fg & 0x1F) - (bg & 0x1F)) * p // self.steps)
        )

    def add_char(self, c):
        self.input_chars.insert(self.pos, c)
        self.pos += 1

    def del_char(self, dir=-1):
        if dir == -1 and self.pos > 0:
            self.pos -= 1
            self.input_chars.pop(self.pos)
        elif dir == 1 and self.pos < len(self.input_chars):
            self.input_chars.pop(self.pos)

    def clear(self):
        self.input_chars.clear()
        self.pos = 0

    def get_text(self):
        return "".join(self.input_chars)

    def get_visible_text(self, max_len=28):
        if self.pos < max_len:
            return self.get_text()[-max_len:]
        else:
            return self.get_text()[self.pos - max_len:self.pos]
