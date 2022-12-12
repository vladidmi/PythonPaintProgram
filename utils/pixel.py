from .settings import *

class Pixel:
    def __init__(self, pixel_x, pixel_y, color, type_structure=None, status=None):
        self.pixel_x = pixel_x
        self.pixel_y = pixel_y
        self.color = color
        self.type_structure = type_structure
        self.status = status
        self.history = dict()