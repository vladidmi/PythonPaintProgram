from .settings import *
from .button import *

class Pixel:
    def __init__(self, pixel_x, pixel_y, color=None, type_structure=None, tact = None, status=None):
        self.pixel_x = pixel_x
        self.pixel_y = pixel_y
        self.color = color
        self.type_structure = type_structure
        if not status:
            self.status = dict()
        else:
            self.status = status
        self.tact = tact
        self.history = dict()
    
    def get_color(self, current_mode):
        if current_mode == PLAN:
            if self.type_structure:
                return self.color
            elif self.tact:
                return tact_button_colors[self.tact-1]
        elif current_mode != TACT:
            return self.color
        elif self.tact != None:
            return tact_button_colors[self.tact-1]
        else:
            return None
    
    def draw_color(self, win,current_color,i,j):
        #drawing with transparency (https://stackoverflow.com/questions/6339057/draw-a-transparent-rectangles-and-polygons-in-pygamepyg)
        s = pygame.Surface((PIXEL_SIZE,PIXEL_SIZE)) # the size of the rect
        s.set_alpha(int(TRANSPARENCY*256)) # alpha level
        s.fill(current_color) # this fills the entire surface
        win.blit(s, (j * PIXEL_SIZE,i *
                                    PIXEL_SIZE)) # the top-left coordinates