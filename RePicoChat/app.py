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
    """
    A class to manage display operations using a given color palette.

    Attributes:
        palette (Palette): The color palette used for display colors.
        display (_Display): The internal display object for rendering.
        BG_COLOR_DARK (int): Dark background color.
        BG_COLOR (int): Background color.
        FG_COLOR_DARK (int): Dark foreground color.
        FG_COLOR (int): Foreground color.
        TEXT_COLOR_DARK (int): Dark text color.
        TEXT_COLOR (int): Text color.
        TEXT_SHADOW_COLOR_DARK (int): Dark text shadow color.
        TEXT_SHADOW_COLOR (int): Text shadow color.
        DISPLAY_WIDTH (int): Width of the display.
        DISPLAY_HEIGHT (int): Height of the display.
        CHAR_WIDTH (int): Width of a character.

    Methods:
        alert(text: str) -> None: Displays an alert message centered on the screen.
        clear() -> None: Clears the display with the background color.
        color565(red: int, green: int = 0, blue: int = 0) -> int: Converts RGB values to 565 color format.
    """

    def __init__(self, palette: Palette) -> None:
        """Initialize the Display object with a given color palette.

        Sets up the display attributes using colors from the provided palette
        and initializes the internal display object for rendering.

        Args:
            palette (Palette): The color palette used for setting display colors.
        """
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
        """
        Displays an alert message centered on the screen.

        The text is split into lines that fit within the display width,
        and each line is centered horizontally. The message is vertically
        centered on the display. The display is cleared before showing
        the message.

        Args:
            text (str): The alert message to display.
        """
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
        """
        Clear the display by filling it with the background color and updating the screen.
        """
        self.display.fill(self.BG_COLOR)
        self.display.show()

    @staticmethod
    def color565(red: int, green: int = 0, blue: int = 0) -> int:
        """
        Convert RGB values to a 16-bit 565 color format.

        This method takes red, green, and blue color components and converts
        them into a single 16-bit integer representing the color in 565 format.
        If a tuple or list is provided as the red argument, it extracts the
        first three elements as the RGB components.

        Args:
            red (int or tuple or list): The red component of the color, or a
                tuple/list containing the RGB components.
            green (int, optional): The green component of the color. Defaults to 0.
            blue (int, optional): The blue component of the color. Defaults to 0.

        Returns:
            int: The 16-bit integer representing the color in 565 format.
        """
        if isinstance(red, (tuple, list)):
            red, green, blue = red[:3]
        return (red & 0xF8) << 8 | (green & 0xFC) << 3 | blue >> 3


class App:
    """
    A class representing an application with optional WLAN connectivity.

    Attributes:
        app_name (str): The name of the application.
        _enable_wlan (bool): Flag to enable WLAN connectivity.
        config (Config): Configuration object for the application.
        display (Display): Display object for rendering UI.
        userinput (UserInput): User input handler.
        nic (network.WLAN or None): WLAN network interface controller.

    Methods:
        init_wifi(): Initializes and connects to a WIFI network.
        quit(): Displays a goodbye message and resets the device.
    """

    def __init__(self, app_name: str = "Sample App", enable_wlan: bool = False) -> None:
        """
        Initialize the App instance with optional WLAN connectivity.

        Args:
            app_name (str): The name of the application. Defaults to "Sample App".
            enable_wlan (bool): Flag to enable WLAN connectivity. Defaults to False.

        Initializes the configuration, display, and user input components.
        If WLAN is enabled, attempts to create a WLAN object and connect to a network.
        Clears the display after initialization.
        """
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
        """
        Initialize and connect to a WIFI network.

        Activates the WIFI module if it is not already active and attempts to
        connect to the specified WIFI network using credentials from the
        configuration. Alerts are displayed for each step of the process,
        including errors and retries. Checks for internet connectivity by
        making a request to an external service and retries if necessary.
        """
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
        """
        Display a goodbye message and reset the device.

        This method shows a "Bye!" alert on the display, waits for a short
        duration, and then resets the device to restart the application.
        """
        self.display.alert("Bye!")
        time.sleep(1)
        reset()
