import asyncio
import random
import requests

from lib.hydra.config import Config

from . import base64 as b64


class PicoChatConfig:
    def __init__(self, hydra_config: Config = Config()):
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
    def __init__(self, pico_chat_config: PicoChatConfig) -> None:
        self.on_new_messages = None
        self._config = pico_chat_config
        self._last_messages = []

    @staticmethod
    def wrap_text(text: str, width: int = 30) -> list:
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
        return random.uniform(0, 1)

    def get_messages(self) -> list:
        response = requests.get(f'https://{self._config.server}/{self.validator}/%2bget', headers={})
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
        clean_message = message.strip()
        if not clean_message:
            return False
        encoded = b64.b32encode(f"<{self._config.username}> {clean_message}\n".encode()).decode("ascii")
        requests.get(f'https://{self._config.server}/{self.validator}/{encoded}', headers={})
        return True

    def update(self, get_messages: bool = True):
        messages = self.get_messages() if get_messages else self._last_messages
        if messages != self._last_messages or get_messages is False:
            self._last_messages = messages
            if self.on_new_messages:
                self.on_new_messages(messages)

    async def start_polling(self, interval: int = 5) -> None:
        while True:
            self.update()
            await asyncio.sleep(interval)
