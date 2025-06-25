import gc
import network
import requests
import time


class Display:
    def __init__(self, palette):
        self.palette = palette
        from lib.display import Display
        self.display = Display()

        self.BG_COLOR = self.palette[2]
        self.BG_COLOR_DARK = self.palette[1]
        self.FG_COLOR = self.palette[4]
        self.FG_COLOR_DARK = self.palette[3]
        self.TEXT_COLOR = self.palette[8]
        self.TEXT_COLOR_DARK = self.palette[7]
        self.TEXT_SHADOW_COLOR = self.palette[6]
        self.TEXT_SHADOW_COLOR_DARK = self.palette[5]

        self.DISPLAY_WIDTH = 240
        self.DISPLAY_HEIGHT = 135
        self.CHAR_WIDTH = 8

    def alert(self, text):
        self.clear()
        words = text.split()
        lines = []
        line = ""
        for word in words:
            if len(line) + len(word) + 1 <= self.DISPLAY_WIDTH // 8:
                line += (" " if line else "") + word
            else:
                lines.append(line)
                line = word
        if line:
            lines.append(line)

        y = (self.DISPLAY_HEIGHT - len(lines) * 12) // 2
        for l in lines:
            x = (self.DISPLAY_WIDTH - len(l) * 8) // 2
            self.display.text(l, x, y, self.TEXT_COLOR)
            y += 12
        self.display.show()

    def clear(self):
        self.display.fill(self.BG_COLOR)
        self.display.show()

    def text_width(self, text):
        return len(text) * self.CHAR_WIDTH

    @staticmethod
    def color565(r, g=0, b=0):
        if isinstance(r, (tuple, list)):
            r, g, b = r[:3]
        return (r & 0xF8) << 8 | (g & 0xFC) << 3 | b >> 3


class App:
    def __init__(self, app_name="Sample App", enable_wlan=False):
        self.app_name = app_name
        from lib.hydra.config import Config
        self.config = Config()
        self.display = Display(self.config.palette)
        from lib.userinput import UserInput
        self.userinput = UserInput()
        self.nic = None

        if enable_wlan:
            try:
                self.nic = network.WLAN(network.STA_IF)
            except Exception:
                self.display.alert("WiFi init failed")
                time.sleep(2)
                return
            self.init_wifi()

        self.display.clear()
        gc.collect()

    def init_wifi(self):
        self.display.alert("Turning on WIFI module...")
        self.nic.active(True)
        if not self.nic.isconnected():
            try:
                self.display.alert(f"Attempting to connect to WIFI network {self.config['wifi_ssid']}...")
                self.nic.connect(self.config["wifi_ssid"], self.config["wifi_pass"])
            except Exception as err:
                self.display.alert(f"Error encountered during WIFI connection: {err}")
                time.sleep(5)
                return

        for i in range(1, 6):
            try:
                self.display.alert("Checking internet connectivity...")
                r = requests.get("http://1.1.1.1/")
                if r.status_code == 200:
                    self.display.alert("Internet connection established successfully!")
                    break
            except Exception as err:
                if i > 2:
                    self.display.alert(f"[{i}] Retrying internet connectivity check: {err}")
                time.sleep(1)

        gc.collect()

    def quit(self):
        self.display.alert("Bye")
        time.sleep(1)
        import machine
        machine.reset()
