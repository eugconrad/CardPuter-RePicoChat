import asyncio
import random
import requests

from lib.hydra.config import Config

from . import base64 as b64


class PicoChatConfig:
    """
    PicoChatConfig manages configuration settings specific to the PicoChat application.

    This class provides properties to access and modify the server and username settings
    within the shared MicroHydra configuration. It ensures default values are set if
    these settings are not already present and saves changes back to the configuration file.
    """

    def __init__(self, hydra_config: Config = Config()):
        """
        Initialize a PicoChatConfig instance with a given MicroHydra configuration.

        Parameters:
        hydra_config (Config): An instance of the MicroHydra Config class, defaulting to a singleton instance.
        """
        self._config = hydra_config

    @property
    def server(self):
        if "pico_chat_server" not in self._config.config:
            self._config["pico_chat_server"] = "picochat-server.fly.dev"
            return self._config["pico_chat_server"]
        else:
            return self._config["pico_chat_server"]

    @server.setter
    def server(self, value: str):
        self._config["pico_chat_server"] = str(value)
        self._config.save()

    @property
    def username(self):
        if "pico_chat_username" not in self._config.config:
            self._config["pico_chat_username"] = f"User_{random.randint(1000, 9999)}"
            return self._config["pico_chat_username"]
        else:
            return self._config["pico_chat_username"]

    @username.setter
    def username(self, value: str):
        self._config["pico_chat_username"] = str(value)
        self._config.save()


class PicoChatClient:
    """
    PicoChatClient handles communication with the PicoChat server.

    This class provides methods to send and receive messages, manage message history,
    and continuously poll the server for new messages. It utilizes the PicoChatConfig
    for server and username configurations. The client can wrap text for display,
    validate server connections, and encode/decode messages using base32 encoding.
    """

    def __init__(self, pico_chat_config: PicoChatConfig) -> None:
        """
        Initializes a PicoChatClient instance with the given configuration.

        Sets up the client with the specified PicoChatConfig, initializes
        the message callback to None, and prepares an empty list for storing
        the last received messages.

        Args:
            pico_chat_config (PicoChatConfig): The configuration for the PicoChat server.
        """
        self.on_new_messages = None
        self._config = pico_chat_config
        self._last_messages = []

    @staticmethod
    def wrap_text(text: str, width: int = 30) -> list:
        """
        Wraps the input text into lines of a specified maximum width.

        Splits the input text into words and arranges them into lines,
        ensuring that each line does not exceed the specified width.
        The default width is 30 characters.

        Args:
            text (str): The text to be wrapped.
            width (int, optional): The maximum width of each line. Defaults to 30.

        Returns:
            list: A list of strings, each representing a line of wrapped text.
        """
        words = str(text).split(' ')
        lines = []
        current = ""
        for word in words:
            if len(current) + len(word) + 1 < width:
                current += word + " "
            else:
                lines.append(current)
                current = word + " "
        lines.append(current)
        return lines

    @property
    def validator(self) -> float:
        """
        Generates a random float between 0 and 1.

        This property is used to create a unique identifier for server requests,
        ensuring variability in the request URL.

        Returns:
            float: A random float value between 0 and 1.
        """
        return random.uniform(0, 1)

    def get_messages(self) -> list:
        """
        Retrieves the latest messages from the PicoChat server.

        Sends a GET request to the server to fetch the latest chat messages.
        If the server responds with a 204 status code, indicating no new messages,
        it returns the last cached messages. Otherwise, it decodes the received
        messages using base32 decoding and returns them as a list of strings.

        Returns:
            list: A list of decoded chat messages.
        """
        response = requests.get(f'https://{self._config.server}/{self.validator}/%2bget', headers={})
        if response.status_code == 204:
            return self._last_messages
        rawlog = response.content.decode("ascii")
        splitlog = rawlog.split('-')[-15:]
        chatlog = []
        for msg in splitlog:
            try:
                decoded = b64.b32decode(msg).decode("ascii")
                chatlog.append(decoded.strip())
            except:
                continue
        return chatlog

    def send_message(self, message: str) -> bool:
        """
        Sends a message to the PicoChat server.

        Strips the input message of leading and trailing whitespace, encodes it
        using base32 encoding with the username, and sends it to the server.
        Returns False if the message is empty after stripping.

        Args:
            message (str): The message to be sent.

        Returns:
            bool: True if the message was sent successfully, False if the message was empty.
        """
        clean_message = message.strip()
        if not clean_message:
            return False
        encoded = b64.b32encode(f"<{self._config.username}> {clean_message}\n".encode()).decode("ascii")
        requests.get(f'https://{self._config.server}/{self.validator}/{encoded}', headers={})
        return True

    def update(self, get_messages: bool = True):
        """
        Updates the message history by retrieving new messages from the server.

        If `get_messages` is True, fetches the latest messages from the server;
        otherwise, uses the last cached messages. If the new messages differ
        from the cached ones or `get_messages` is False, updates the cached
        messages and triggers the `on_new_messages` callback if it is set.

        Args:
            get_messages (bool, optional): Flag to determine whether to fetch
            new messages from the server. Defaults to True.
        """
        messages = self.get_messages() if get_messages else self._last_messages
        if messages != self._last_messages or get_messages is False:
            self._last_messages = messages
            if self.on_new_messages:
                self.on_new_messages(messages)

    async def start_polling(self, interval: int = 5) -> None:
        """
        Continuously polls the PicoChat server for new messages at a specified interval.

        This asynchronous method repeatedly calls the `update` method to refresh
        the message history and then waits for the specified interval before
        repeating the process.

        Args:
            interval (int, optional): The time in seconds to wait between polling
            the server for new messages. Defaults to 5.
        """
        while True:
            self.update()
            await asyncio.sleep(interval)
