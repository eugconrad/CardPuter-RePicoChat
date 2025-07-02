import random
import requests

from . import base64 as b64


class Client:
    def __init__(self, config):
        self.messages = []
        self.on_request_start = None
        self.on_request_end = None
        self.on_update = None
        self.on_new_message = None
        self._config = config

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
        return self._parse_messages(raw)

    def send_message(self, text: str):
        text = text.strip()
        if not text:
            return self.messages
        data = f"<{self._config.username}> {text}\n"
        encoded = b64.b32encode(data.encode()).decode()
        raw = self._fetch(encoded)
        if not raw:
            return self.messages
        return self._parse_messages(raw)

    def update(self, messages):
        if self.on_update:
            self.on_update(messages)
        if self.on_new_message and messages != self.messages:
            self.on_new_message()
        self.messages = messages
