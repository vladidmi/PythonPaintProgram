from .settings import *
from .button import *


class Pixel:
    def __init__(
        self, pixel_x, pixel_y, color=None, type_structure=None, tact=None, status=None
    ):
        self.pixel_x = pixel_x
        self.pixel_y = pixel_y
        self.color = color
        self.type_structure = type_structure
        if not status:
            self.status = dict()
        else:
            self.status = status
        self.tact = tact

    def __str__(self):
        return f"{self.pixel_x}-{self.pixel_y},{self.type_structure},{self.status}"

    def get_color_key(self, current_mode, current_day):
        if current_mode == PLAN:
            if not self.type_structure and not self.tact:
                return None, None
            elif not self.type_structure:
                return self.tact, TRANSPARENT
            elif not self.status:
                return self.type_structure, TRANSPARENT
            else:
                for step in list(self.status)[::-1]:
                    if self.status[step] and max(self.status[step]) < current_day:
                        return step, TRANSPARENT
                    elif self.status[step] and max(self.status[step]) == current_day:
                        return step, SEMI_TRANSPARENT
                return self.type_structure, TRANSPARENT
        elif current_mode == DRAW_SCTRUCTURE:
            return self.type_structure, SEMI_TRANSPARENT
        elif current_mode == TACT:
            return self.tact, SEMI_TRANSPARENT

    def draw_color(self, win, current_color_key, transparency_level, i, j):
        # drawing with transparency (https://stackoverflow.com/questions/6339057/draw-a-transparent-rectangles-and-polygons-in-pygamepyg)
        s = pygame.Surface((PIXEL_SIZE, PIXEL_SIZE))  # the size of the rect
        s.set_alpha(int(transparency_level * 256))  # alpha level
        s.fill(all_colors[current_color_key])  # this fills the entire surface
        win.blit(s, (j * PIXEL_SIZE, i * PIXEL_SIZE))  # the top-left coordinates
