from .settings import *

class Button:
    def __init__(self, x=0, y=0, width = 50, height = 50, color = WHITE, text=None, text_color=BLACK, label=None):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.text = text
        self.text_color = text_color
        self.label = label

    def draw(self, win):
        pygame.draw.rect(
            win, self.color, (self.x, self.y, self.width, self.height))
        pygame.draw.rect(
            win, BLACK, (self.x, self.y, self.width, self.height), 2)
        if self.text:
            button_font = get_font(10)
            text_surface = button_font.render(self.text, 1, self.text_color)
            win.blit(text_surface, (self.x + self.width /
                                    2 - text_surface.get_width()/2, self.y + self.height/2 - text_surface.get_height()/2))

    def clicked(self, pos, current_mode):
        x, y = pos
        if self.label not in DRAWING_MODES[current_mode]:
            return False
        if not (x >= self.x and x <= self.x + self.width):
            return False
        if not (y >= self.y and y <= self.y + self.height):
            return False

        return True

button_y = HEIGHT + BOX_SIZE//2

#COMMON
ERASE = 'Erase'
CLEAR = 'Clear'
BIGGER = 'Bigger'
SMALLER = 'Smaller'
DRAW_MODE = 'Draw mode'

common_buttons = {
    ERASE:Button(y=button_y, width=BOX_SIZE, height=BOX_SIZE, color=WHITE, text = ERASE,  label = ERASE),
    CLEAR:Button(y=button_y, width=BOX_SIZE, height=BOX_SIZE, color= WHITE, text = CLEAR,  label = CLEAR),
    BIGGER:Button(y=button_y, width=BOX_SIZE, height=BOX_SIZE, color= WHITE, text = BIGGER, label = BIGGER),
    SMALLER:Button(y=button_y, width=BOX_SIZE, height=BOX_SIZE, color= WHITE, text = SMALLER,  label = SMALLER),
    DRAW_MODE:Button(y=button_y, width=BOX_SIZE, height=BOX_SIZE, color= WHITE, text = DRAW_MODE,  label = DRAW_MODE),
}

#Drawing structure
CONCRETE = 'Beton'
PREFABRICATED_PART = 'Feftigteil'
MASONRY = 'Mauer'

draw_structure_buttons = {
    CONCRETE:Button(y=button_y, width=BOX_SIZE, height=BOX_SIZE, color=BLACK, text = CONCRETE, text_color= WHITE, label = CONCRETE),
    PREFABRICATED_PART:Button(y=button_y, width=BOX_SIZE, height=BOX_SIZE, color=RED, text = PREFABRICATED_PART, text_color= WHITE, label = PREFABRICATED_PART),
    MASONRY:Button(y=button_y, width=BOX_SIZE, height=BOX_SIZE, color=GREEN, text = MASONRY, text_color= WHITE, label = MASONRY),
}

#Plannuing
FORMWORK = 'Schalen'
REINFORCE = 'Bewehren'
POUR_CONCRETE ='Betonieren'
PREFABRICATED_PART_ASSEMBLE = 'Fertigteil setzen'
DO_MASONRY = 'Mauern'
PART_COMPLETE = 'Fertig'
LAST_DAY = 'Last day'
NEXT_DAY = 'Next day'

plan_buttons = {
    FORMWORK:Button(y=button_y, width=BOX_SIZE, height=BOX_SIZE, color=YELLOW, text = FORMWORK, label = FORMWORK),
    REINFORCE:Button(y=button_y, width=BOX_SIZE, height=BOX_SIZE, color=LIGHT_BLUE, text = REINFORCE, label = REINFORCE),
    POUR_CONCRETE:Button(y=button_y, width=BOX_SIZE, height=BOX_SIZE, color= LIGHT_GREEN, text = POUR_CONCRETE, label = POUR_CONCRETE),
    PREFABRICATED_PART_ASSEMBLE:Button(y=button_y, width=BOX_SIZE, height=BOX_SIZE, color=VIOLET, text = PREFABRICATED_PART_ASSEMBLE, label = PREFABRICATED_PART_ASSEMBLE),
    DO_MASONRY:Button(y=button_y, width=BOX_SIZE, height=BOX_SIZE, color=ORANGE, text = DO_MASONRY, label = DO_MASONRY),
    PART_COMPLETE:Button(y=button_y, width=BOX_SIZE, height=BOX_SIZE, color= DARK_RED, text = PART_COMPLETE, label = PART_COMPLETE),    
    LAST_DAY:Button(y=button_y, width=BOX_SIZE, height=BOX_SIZE, color= WHITE, text = LAST_DAY,  label = LAST_DAY),
    NEXT_DAY:Button(y=button_y, width=BOX_SIZE, height=BOX_SIZE, color= WHITE, text = NEXT_DAY,  label = NEXT_DAY),
}

#Tact division
number_of_tacts = 2
tact_id = None
TACT = 'Taktber.'
tact_add = 'Takt+'
tact_delete = 'Takt-'
tact_button_options = {
    tact_add: Button(y=button_y, width=BOX_SIZE, height=BOX_SIZE, color=WHITE, text = tact_add, label = tact_add),
    tact_delete: Button(y=button_y, width=BOX_SIZE, height=BOX_SIZE, color=WHITE, text = tact_delete, label = tact_delete),
}
tact_button_colors = [BLUE, ORANGE, VIOLET, GREY, YELLOW, BROWN]
tact_buttons = {
    f'{TACT} {i+1}': Button(y=button_y, width=BOX_SIZE, height=BOX_SIZE, color=tact_button_colors[i], text = f'{TACT} {i+1}', label = f'{TACT} {i+1}') 
    for i in range(number_of_tacts)
}

DRAWING_COLOR_ORDER = [
    None, BLACK, YELLOW, LIGHT_BLUE, LIGHT_GREEN, DARK_RED, 
    None, RED, VIOLET, DARK_RED, 
    None, GREEN, ORANGE, DARK_RED, None,
    ]

DRAWING_MODES = {
    'Draw structure':{**common_buttons, **draw_structure_buttons},
    'Plan':{**common_buttons, **plan_buttons},
    'Tact':{**common_buttons, **tact_button_options, **tact_buttons},
    }