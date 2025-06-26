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
        self.callback = None
        self.messages = []
        self.on_request_start = None
        self.on_request_end = None
        self._config = pico_chat_config

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

    @staticmethod
    def _parse_messages(raw):
        msgs = []
        for m in raw.split('-')[-15:]:
            try:
                d = b64.b32decode(m).decode().strip()
                msgs.append(d)
            except:
                pass
        return msgs

    @property
    def _validator(self):
        return random.random()

    def _fetch(self, path):
        if self.on_request_start:
            self.on_request_start()
        try:
            r = requests.get(f'https://{self._config.server}/{self._validator}/{path}')
            if r.status_code == 204:
                return None
            return r.content.decode()
        except:
            return None
        finally:
            if self.on_request_end:
                self.on_request_end()

    def get_messages(self):
        raw = self._fetch('%2bget')
        if not raw:
            return self.messages
        self.messages = self._parse_messages(raw)
        return self.messages

    def send_message(self, text: str):
        text = text.strip()
        if not text:
            return False
        data = f"<{self._config.username}> {text}\n"
        encoded = b64.b32encode(data.encode()).decode()
        raw = self._fetch(encoded)
        if not raw:
            return self.messages
        self.messages = self._parse_messages(raw)
        return self.messages

    def update(self, get=True):
        msgs = self.get_messages() if get else self.messages
        self.messages = msgs
        if self.callback:
            self.callback(msgs)
