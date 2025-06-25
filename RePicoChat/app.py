import time
import network
import requests

from machine import Pin, reset
from micropython import const

from lib.display import Display as _Display
from lib.display.palette import Palette as Palette
from lib.userinput import UserInput as UserInput
from lib.hydra.config import Config as Config


class Display:
    def __init__(self, palette: Palette) -> None:
        self.palette = palette
        self.display = _Display()

        self.BG_COLOR_DARK = const(self.palette[1])
        self.BG_COLOR = const(self.palette[2])
        self.FG_COLOR_DARK = const(self.palette[3])
        self.FG_COLOR = const(self.palette[4])
        self.TEXT_COLOR_DARK = const(self.palette[7])
        self.TEXT_COLOR = const(self.palette[8])
        self.TEXT_SHADOW_COLOR_DARK = const(self.palette[5])
        self.TEXT_SHADOW_COLOR = const(self.palette[6])

        self.DISPLAY_WIDTH = const(240)
        self.DISPLAY_HEIGHT = const(135)
        self.CHAR_WIDTH = const(8)

    def alert(self, text: str) -> None:
        self.clear()
        words = text.split()
        lines = []
        current_line = ""
        for word in words:
            if len(current_line) + len(word) + 1 <= self.DISPLAY_WIDTH // 8:
                current_line += (" " if current_line else "") + word
            else:
                lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)
        line_spacing = 12
        y = (self.DISPLAY_HEIGHT - len(lines) * line_spacing) // 2
        for line in lines:
            x = (self.DISPLAY_WIDTH - len(line) * 8) // 2
            self.display.text(line, x, y, self.TEXT_COLOR)
            y += line_spacing
        self.display.show()

    def clear(self) -> None:
        self.display.fill(self.BG_COLOR)
        self.display.show()

    @staticmethod
    def color565(red: int, green: int = 0, blue: int = 0) -> int:
        if isinstance(red, (tuple, list)):
            red, green, blue = red[:3]
        return (red & 0xF8) << 8 | (green & 0xFC) << 3 | blue >> 3


class App:
    def __init__(self, app_name: str = "Sample App", enable_wlan: bool = False) -> None:
        self.app_name = app_name
        self._enable_wlan = enable_wlan

        self.config = Config()
        self.display = Display(palette=self.config.palette)
        self.userinput = UserInput()

        if self._enable_wlan:
            try:
                self.nic = network.WLAN(network.STA_IF)
            except RuntimeError as e:
                self.display.alert(str(e))
                try:
                    self.nic = network.WLAN(network.STA_IF)
                except RuntimeError as e:
                    self.nic = None
                    self.display.alert("Wifi WLAN object couldnt be created")
                    time.sleep(2)
                    self.display.alert(str(e))
                    time.sleep(5)
                    reset()
            self.init_wifi()
        else:
            self.nic = None

        self.display.clear()

        # self.PIN_QUIT = Pin(0, Pin.IN, Pin.PULL_DOWN)
        # self.PIN_QUIT.irq(handler=lambda _: self.quit(), trigger=Pin.IRQ_RISING)

    def init_wifi(self):
        self.display.alert('Turning on WIFI module...')

        if not self.nic.active():
            self.nic.active(True)

        if not self.nic.isconnected():
            try:
                self.display.alert('Attempting to connect to WIFI network...')
                self.nic.connect(self.config['wifi_ssid'], self.config['wifi_pass'])
            except OSError as e:
                self.display.alert("Error encountered during WIFI connection attempt.")
                time.sleep(2)
                self.display.alert(str(e))
                time.sleep(3)

        self.display.alert(f'Connected to WIFI network: {self.config["wifi_ssid"]}')

        i = 1
        while i < 20:
            try:
                self.display.alert('Checking internet connectivity...')
                response = requests.get("https://ident.me/")
                if response.status_code == 200:
                    self.display.alert("Internet connection established successfully!")
                    break
            except Exception as err:
                self.display.alert(f"Retrying internet connectivity check... (Attempt {i})")
                i += 1
                time.sleep(1)
                continue

    def quit(self):
        self.display.alert("Bye!")
        time.sleep(1)
        reset()
