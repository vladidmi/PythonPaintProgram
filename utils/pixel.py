from .settings import *


class Pixel:
    def __init__(
        self,
        pixel_x,
        pixel_y,
        type_structure=None,
        tact=None,
        status=None,
        tk_rect=None,
    ):
        self.pixel_x = pixel_x
        self.pixel_y = pixel_y
        self.type_structure = type_structure
        if not status:
            self.status = dict()
        else:
            self.status = status
        self.tact = tact
        self.tk_rect = tk_rect

    def __str__(self):
        return f"{self.pixel_x}-{self.pixel_y},{self.type_structure},{self.status}"

    def get_color_key_for_plan(self, current_mode, current_day):
        if current_mode == PLAN:
            if self.status:
                for step in list(self.status)[::-1]:
                    if (
                        self.status[step]
                        and max(self.status[step]) < current_day
                        and step != NEW_EVENT
                    ):
                        return step, TRANSPARENT
            if self.type_structure:
                return self.type_structure, TRANSPARENT
        elif current_mode == TACT and not self.tact and self.type_structure:
            return self.type_structure, TRANSPARENT
        return None, None

    def get_color_key_for_print(self, weekday):
        if (
            PART_COMPLETE in self.status
            and self.status[PART_COMPLETE]
            and pd.Timestamp(weekday) >= max(self.status[PART_COMPLETE])
        ):
            return PART_COMPLETE, NOT_TRANSPARENT
        if self.status:
            for step in list(self.status)[::-1]:
                if self.status[step] and pd.Timestamp(weekday) in self.status[step]:
                    return step, NOT_TRANSPARENT

        return None, None

    @staticmethod
    def draw_color(current_color_key, transparency_level, i, j):
        pass
