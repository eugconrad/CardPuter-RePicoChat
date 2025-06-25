import asyncio
import random
import requests

from lib.hydra.config import Config
from . import base64 as b64


class PicoChatConfig:
    def __init__(self, hydra_config=Config()):
        self._config = hydra_config

    @property
    def server(self):
        key = "pico_chat_server"
        if key not in self._config.config:
            self._config[key] = "picochat-server.fly.dev"
        return self._config[key]

    @server.setter
    def server(self, value):
        self._config["pico_chat_server"] = str(value)
        self._config.save()

    @property
    def username(self):
        key = "pico_chat_username"
        if key not in self._config.config:
            self._config[key] = "User_" + str(random.randint(1000, 9999))
        return self._config[key]

    @username.setter
    def username(self, value):
        self._config["pico_chat_username"] = str(value)
        self._config.save()


class PicoChatClient:
    def __init__(self, pico_chat_config):
        self.on_new_messages = None
        self._config = pico_chat_config
        self._last_messages = []

    @staticmethod
    def wrap_text(text, width=30):
        words = str(text).split(' ')
        lines = []
        line = ""
        for w in words:
            if len(line) + len(w) + 1 < width:
                line += w + " "
            else:
                lines.append(line)
                line = w + " "
        lines.append(line)
        return lines

    @property
    def validator(self):
        return random.random()

    def get_messages(self):
        try:
            r = requests.get(f'https://{self._config.server}/{self.validator}/%2bget')
            if r.status_code == 204:
                return self._last_messages
            raw = r.content.decode()
        except:
            return self._last_messages

        msgs = []
        for m in raw.split('-')[-15:]:
            try:
                d = b64.b32decode(m).decode().strip()
                msgs.append(d)
            except:
                pass
        return msgs

    def send_message(self, msg):
        msg = msg.strip()
        if not msg:
            return False
        data = f"<{self._config.username}> {msg}\n"
        enc = b64.b32encode(data.encode()).decode()
        try:
            requests.get(f'https://{self._config.server}/{self.validator}/{enc}')
            return True
        except:
            return False

    def update(self, get=True):
        msgs = self.get_messages() if get else self._last_messages
        if msgs != self._last_messages or not get:
            self._last_messages = msgs
            if self.on_new_messages:
                self.on_new_messages(msgs)

    async def start_polling(self, interval=5):
        while True:
            self.update()
            await asyncio.sleep(interval)
