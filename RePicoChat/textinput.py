class Cursor:
    def __init__(self, color_bg, color_fg):
        self.blink = 500
        self.pos = 0

        self.color_bg = color_bg
        self.color_fg = color_fg

        self.direction = 1
        self.step = 0
        self.steps = 50

    def to_start(self):
        self.pos = 0

    def to_end(self, length=28):
        self.pos = min(length, 28)

    def move(self, direction, max_len=28):
        self.pos = max(0, min(self.pos + direction, max_len))

    def tick(self) -> int:
        self.step = (self.step + 1) % (self.steps * 2)
        direction = 1 if self.step < self.steps else -1
        progress = (self.step % self.steps) / self.steps

        def get_components(color):
            return (color >> 8) & 0xF8, (color >> 3) & 0xFC, (color << 3) & 0xF8

        bg_r, bg_g, bg_b = get_components(self.color_bg)
        fg_r, fg_g, fg_b = get_components(self.color_fg)
        r = bg_r + int((fg_r - bg_r) * (progress if direction > 0 else 1 - progress))
        g = bg_g + int((fg_g - bg_g) * (progress if direction > 0 else 1 - progress))
        b = bg_b + int((fg_b - bg_b) * (progress if direction > 0 else 1 - progress))
        return (r << 8) & 0xF800 | (g << 3) & 0x07E0 | (b >> 3)

    @property
    def x(self):
        return min(self.pos, 28) * 8


class TextInputManager:
    def __init__(self, cursor: Cursor):
        self.input_chars = []
        self.cursor = cursor

    def add_char(self, c):
        self.input_chars.insert(self.cursor.pos, c)
        self.cursor.pos += 1

    def del_char(self, dir=-1):
        if dir == -1 and self.cursor.pos > 0:
            self.cursor.pos -= 1
            self.input_chars.pop(self.cursor.pos)
        elif dir == 1 and self.cursor.pos < len(self.input_chars):
            self.input_chars.pop(self.cursor.pos)

    def move_cursor(self, d):
        self.cursor.move(d, len(self.input_chars))

    def reset_cursor(self):
        self.cursor.to_start()

    def end_cursor(self):
        self.cursor.to_end(len(self.input_chars))

    def clear(self):
        self.input_chars.clear()
        self.cursor.to_start()

    def get_text(self):
        return "".join(self.input_chars)

    def get_visible_text(self, max_len=28):
        if self.cursor.pos < max_len:
            return self.get_text()[-max_len:]
        else:
            return self.get_text()[self.cursor.pos - max_len:self.cursor.pos]
