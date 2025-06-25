class TextInputManager:
    class Cursor:
        def __init__(self):
            self.pos = 0
            self.blink_timer = 100
            self.visible = True

        def to_start(self):
            self.pos = 0

        def to_end(self, length: int = 25):
            self.pos = length

        def move(self, direction: int, max_len: int = 25):
            if direction < 0 < self.pos:
                self.pos -= 1
            elif direction > 0 and self.pos < max_len:
                self.pos += 1

        def tick(self):
            self.blink_timer -= 1
            if self.blink_timer <= 0:
                self.blink_timer = 100
                self.visible = not self.visible
            return self.visible

        @property
        def x(self) -> int:
            if self.pos < 25:
                return self.pos * 8 + 8
            else:
                return 25 * 8 + 8

    def __init__(self):
        self.input_text = ""
        self.cursor = self.Cursor()

    def add_char(self, char: str):
        self.input_text = (
                self.input_text[:self.cursor.pos] + char + self.input_text[self.cursor.pos:]
        )
        self.cursor.pos += 1

    def del_char(self, direction: int = -1):
        if direction == -1 and self.cursor.pos > 0:
            self.input_text = (
                    self.input_text[:self.cursor.pos - 1] + self.input_text[self.cursor.pos:]
            )
            self.cursor.pos -= 1
        elif direction == 1 and self.cursor.pos < len(self.input_text):
            self.input_text = (
                    self.input_text[:self.cursor.pos] + self.input_text[self.cursor.pos + 1:]
            )

    def move_cursor(self, direction: int):
        self.cursor.move(direction, len(self.input_text))

    def reset_cursor(self):
        self.cursor.to_start()

    def end_cursor(self):
        self.cursor.to_end(len(self.input_text))

    def clear(self):
        self.input_text = ""
        self.cursor.to_start()

    def get_visible_text(self, max_len: int = 25):
        if self.cursor.pos < max_len:
            return self.input_text[-max_len:]
        else:
            return self.input_text[self.cursor.pos - max_len:self.cursor.pos]
