from .settings import *


class Button:
    def __init__(
        self,
        x=0,
        y=0,
        width=50,
        height=50,
        color=WHITE,
        text=None,
        text_color=BLACK,
        label=None,
    ):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.text = text
        self.text_color = text_color
        self.label = label

    def draw(self, win):
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.height))
        pygame.draw.rect(win, BLACK, (self.x, self.y, self.width, self.height), 2)
        if self.text:
            button_font = get_font(10)
            text_surface = button_font.render(self.text, 1, self.text_color)
            win.blit(
                text_surface,
                (
                    self.x + self.width / 2 - text_surface.get_width() / 2,
                    self.y + self.height / 2 - text_surface.get_height() / 2,
                ),
            )

    def clicked(self, pos, current_mode):
        x, y = pos
        if self.label not in DRAWING_MODES[current_mode]:
            return False
        if not (x >= self.x and x <= self.x + self.width):
            return False
        if not (y >= self.y and y <= self.y + self.height):
            return False

        return True


button_y = HEIGHT + BOX_SIZE // 2

# COMMON
ERASE = "Entf."
CLEAR = "Alles entf."
BIGGER = "Größer"
SMALLER = "Kleiner"
DRAW_MODE = "Modus"
NEXT_FLOOR = "OG+"
PREVIOUS_FLOOR = "OG-"

# Drawing structure
DRAW_SCTRUCTURE = "Draw structure"
CONCRETE = "Beton"
PREFABRICATED_PART = "Feftigteil"
MASONRY = "Mauer"

# Planning
PLAN = "Plan"
FORMWORK = "Schalen"
REINFORCE = "Bewehren"
POUR_CONCRETE = "Betonieren"
PREFABRICATED_PART_ASSEMBLE = "Fertigteil setzen"
DO_MASONRY = "Mauern"
PART_COMPLETE = "Fertig"
LAST_DAY = "Letzter Tag"
NEXT_DAY = "Naechster Tag"

# Tact division
TACT = "BA"
number_of_tacts = 2
tact_id = None
TACT_PART = "BA."
tact_add = "BA+"
tact_delete = "BA-"


# Color_dict
all_colors = {
    # COMMON
    ERASE: WHITE,
    CLEAR: WHITE,
    BIGGER: WHITE,
    SMALLER: WHITE,
    DRAW_MODE: WHITE,
    NEXT_FLOOR: WHITE,
    PREVIOUS_FLOOR: WHITE,
    # Drawing structure
    CONCRETE: BLACK,
    PREFABRICATED_PART: RED,
    MASONRY: GREEN,
    # Planning
    FORMWORK: YELLOW,
    REINFORCE: LIGHT_BLUE,
    POUR_CONCRETE: LIGHT_GREEN,
    PREFABRICATED_PART_ASSEMBLE: VIOLET,
    DO_MASONRY: ORANGE,
    PART_COMPLETE: DARK_RED,
    # Tact division
    f"{TACT_PART} 1": BLUE,
    f"{TACT_PART} 2": ORANGE,
    f"{TACT_PART} 3": VIOLET,
    f"{TACT_PART} 4": GREY,
    f"{TACT_PART} 5": YELLOW,
    f"{TACT_PART} 6": BROWN,
}

# COMMON
common_buttons = {
    ERASE: Button(
        y=button_y,
        width=BOX_SIZE,
        height=BOX_SIZE,
        color=WHITE,
        text=ERASE,
        label=ERASE,
    ),
    CLEAR: Button(
        y=button_y,
        width=BOX_SIZE,
        height=BOX_SIZE,
        color=WHITE,
        text=CLEAR,
        label=CLEAR,
    ),
    BIGGER: Button(
        y=button_y,
        width=BOX_SIZE,
        height=BOX_SIZE,
        color=WHITE,
        text=BIGGER,
        label=BIGGER,
    ),
    SMALLER: Button(
        y=button_y,
        width=BOX_SIZE,
        height=BOX_SIZE,
        color=WHITE,
        text=SMALLER,
        label=SMALLER,
    ),
    DRAW_MODE: Button(
        y=button_y,
        width=BOX_SIZE,
        height=BOX_SIZE,
        color=WHITE,
        text=DRAW_MODE,
        label=DRAW_MODE,
    ),
    PREVIOUS_FLOOR: Button(
        y=button_y,
        width=BOX_SIZE,
        height=BOX_SIZE,
        color=WHITE,
        text=PREVIOUS_FLOOR,
        label=PREVIOUS_FLOOR,
    ),
    NEXT_FLOOR: Button(
        y=button_y,
        width=BOX_SIZE,
        height=BOX_SIZE,
        color=WHITE,
        text=NEXT_FLOOR,
        label=NEXT_FLOOR,
    ),
}

# Drawing structure
draw_structure_buttons = {
    CONCRETE: Button(
        y=button_y,
        width=BOX_SIZE,
        height=BOX_SIZE,
        color=all_colors[CONCRETE],
        text=CONCRETE,
        text_color=WHITE,
        label=CONCRETE,
    ),
    PREFABRICATED_PART: Button(
        y=button_y,
        width=BOX_SIZE,
        height=BOX_SIZE,
        color=all_colors[PREFABRICATED_PART],
        text=PREFABRICATED_PART,
        text_color=WHITE,
        label=PREFABRICATED_PART,
    ),
    MASONRY: Button(
        y=button_y,
        width=BOX_SIZE,
        height=BOX_SIZE,
        color=all_colors[MASONRY],
        text=MASONRY,
        text_color=WHITE,
        label=MASONRY,
    ),
}

# Planning
plan_buttons_options = {
    LAST_DAY: Button(
        y=button_y,
        width=BOX_SIZE,
        height=BOX_SIZE,
        color=WHITE,
        text=LAST_DAY,
        label=LAST_DAY,
    ),
    NEXT_DAY: Button(
        y=button_y,
        width=BOX_SIZE,
        height=BOX_SIZE,
        color=WHITE,
        text=NEXT_DAY,
        label=NEXT_DAY,
    ),
}

plan_buttons = {
    FORMWORK: Button(
        y=button_y,
        width=BOX_SIZE,
        height=BOX_SIZE,
        color=all_colors[FORMWORK],
        text=FORMWORK,
        label=FORMWORK,
    ),
    REINFORCE: Button(
        y=button_y,
        width=BOX_SIZE,
        height=BOX_SIZE,
        color=all_colors[REINFORCE],
        text=REINFORCE,
        label=REINFORCE,
    ),
    POUR_CONCRETE: Button(
        y=button_y,
        width=BOX_SIZE,
        height=BOX_SIZE,
        color=all_colors[POUR_CONCRETE],
        text=POUR_CONCRETE,
        label=POUR_CONCRETE,
    ),
    PREFABRICATED_PART_ASSEMBLE: Button(
        y=button_y,
        width=BOX_SIZE,
        height=BOX_SIZE,
        color=all_colors[PREFABRICATED_PART_ASSEMBLE],
        text=PREFABRICATED_PART_ASSEMBLE,
        label=PREFABRICATED_PART_ASSEMBLE,
    ),
    DO_MASONRY: Button(
        y=button_y,
        width=BOX_SIZE,
        height=BOX_SIZE,
        color=all_colors[DO_MASONRY],
        text=DO_MASONRY,
        label=DO_MASONRY,
    ),
    PART_COMPLETE: Button(
        y=button_y,
        width=BOX_SIZE,
        height=BOX_SIZE,
        color=all_colors[PART_COMPLETE],
        text=PART_COMPLETE,
        label=PART_COMPLETE,
    ),
}

# Tact division
tact_button_options = {
    tact_add: Button(
        y=button_y,
        width=BOX_SIZE,
        height=BOX_SIZE,
        color=WHITE,
        text=tact_add,
        label=tact_add,
    ),
    tact_delete: Button(
        y=button_y,
        width=BOX_SIZE,
        height=BOX_SIZE,
        color=WHITE,
        text=tact_delete,
        label=tact_delete,
    ),
}
tact_button_colors = []
tact_buttons = {
    f"{TACT_PART} {i+1}": Button(
        y=button_y,
        width=BOX_SIZE,
        height=BOX_SIZE,
        color=all_colors[f"{TACT_PART} {i+1}"],
        text=f"{TACT_PART} {i+1}",
        label=f"{TACT_PART} {i+1}",
    )
    for i in range(number_of_tacts)
}

# Modes
DRAWING_MODES = {
    DRAW_SCTRUCTURE: {**common_buttons, **draw_structure_buttons},
    PLAN: {**common_buttons, **plan_buttons_options, **plan_buttons},
    TACT: {**common_buttons, **tact_button_options, **tact_buttons},
}

# Working steps for structures
working_steps = {
    CONCRETE: [FORMWORK, REINFORCE, POUR_CONCRETE, PART_COMPLETE],
    PREFABRICATED_PART: [PREFABRICATED_PART_ASSEMBLE, PART_COMPLETE],
    MASONRY: [DO_MASONRY, PART_COMPLETE],
}

working_steps_flat = set(
    item
    for sublist in [working_steps[key] for key in working_steps]
    for item in sublist
)
