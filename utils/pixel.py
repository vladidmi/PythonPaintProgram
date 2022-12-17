from .settings import *

class Pixel:
    def __init__(self, pixel_x, pixel_y, color=None, type_structure=None, tact = None, status=None):
        self.pixel_x = pixel_x
        self.pixel_y = pixel_y
        self.color = color
        self.type_structure = type_structure
        self.status = status
        self.tact = tact
        self.history = dict()