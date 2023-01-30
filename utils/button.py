from .settings import *


# COMMON
ERASE = "Entf."
SAVE = "Speichern"
BIGGER = "Größer"
SMALLER = "Kleiner"
DRAW_MODE = "Modus"
NEXT_FLOOR = "Ebene +"
PREVIOUS_FLOOR = "Ebene -"
PRINT = "Drucken"

# Drawing structure
DRAW_SCTRUCTURE = "Draw structure"
CONCRETE = "Beton"
PREFABRICATED_PART = "HFT"
MASONRY = "MW"

# Planning
PLAN = "Plan"
FORMWORK = "SCH"
REINFORCE = "BEW"
POUR_CONCRETE = "BET"
PREFABRICATED_PART_ASSEMBLE = "HFT"
DO_MASONRY = "MW"
PART_COMPLETE = "Fertig"
LAST_DAY = "Tag -"
NEXT_DAY = "Tag +"
ACITVE_TACT = "  \\/ Ausgew.BA"  # hint text for the chosen region

# Tact division
TACT = "BA"
number_of_tacts = 6
tact_id = None
TACT_PART = "BA."
tact_add = "BA+"
tact_delete = "BA-"
NO_TACT = "Kein BA"


# Color_dict
all_colors = {
    # COMMON
    ERASE: WHITE,
    SAVE: WHITE,
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
    DRAW_MODE: {
        "color": WHITE,
        "text": DRAW_MODE,
    },
    NEXT_FLOOR: {
        "color": WHITE,
        "text": NEXT_FLOOR,
    },
    PREVIOUS_FLOOR: {
        "color": WHITE,
        "text": PREVIOUS_FLOOR,
    },
    BIGGER: {
        "color": WHITE,
        "text": BIGGER,
    },
    SMALLER: {
        "color": WHITE,
        "text": SMALLER,
    },
    SAVE: {
        "color": WHITE,
        "text": SAVE,
    },
    PRINT: {
        "color": WHITE,
        "text": PRINT,
    },
}

ERASE_BUTTON = {
    "color": WHITE,
    "text": ERASE,
}


# Drawing structure
draw_structure_buttons = {
    CONCRETE: {
        "color": all_colors[CONCRETE],
        "text": CONCRETE,
        "text_color": WHITE,
    },
    PREFABRICATED_PART: {
        "color": all_colors[PREFABRICATED_PART],
        "text": PREFABRICATED_PART,
        "text_color": WHITE,
    },
    MASONRY: {
        "color": all_colors[MASONRY],
        "text": MASONRY,
        "text_color": WHITE,
    },
    ERASE: ERASE_BUTTON,
}

# Planning
plan_buttons_options = {
    LAST_DAY: {
        "color": WHITE,
        "text": LAST_DAY,
    },
    NEXT_DAY: {
        "color": WHITE,
        "text": NEXT_DAY,
    },
}

plan_buttons = {
    FORMWORK: {
        "color": all_colors[FORMWORK],
        "text": FORMWORK,
    },
    REINFORCE: {
        "color": all_colors[REINFORCE],
        "text": REINFORCE,
    },
    POUR_CONCRETE: {
        "color": all_colors[POUR_CONCRETE],
        "text": POUR_CONCRETE,
    },
    PREFABRICATED_PART_ASSEMBLE: {
        "color": all_colors[PREFABRICATED_PART_ASSEMBLE],
        "text": PREFABRICATED_PART_ASSEMBLE,
    },
    DO_MASONRY: {
        "color": all_colors[DO_MASONRY],
        "text": DO_MASONRY,
    },
    PART_COMPLETE: {
        "color": all_colors[PART_COMPLETE],
        "text": PART_COMPLETE,
    },
    ERASE: ERASE_BUTTON,
}

# Tact division
tact_button_options = {
    tact_add: {
        "color": WHITE,
        "text": tact_add,
    },
    tact_delete: {
        "color": WHITE,
        "text": tact_delete,
    },
}

tact_button_colors = []
tact_buttons = {
    NO_TACT: {
        "color": WHITE,
        "text": NO_TACT,
    },
    **{
        f"{TACT_PART} {i+1}": {
            "color": all_colors[f"{TACT_PART} {i+1}"],
            "text": f"{TACT_PART} {i+1}",
        }
        for i in range(number_of_tacts)
    },
}

# Modes
DRAWING_MODES = {
    PLAN: {**plan_buttons_options, **plan_buttons, **tact_buttons},
    DRAW_SCTRUCTURE: {**draw_structure_buttons},
    TACT: {**tact_button_options, **tact_buttons},
}

# Working steps for structures
working_steps = {
    CONCRETE: [FORMWORK, REINFORCE, POUR_CONCRETE, PART_COMPLETE],
    PREFABRICATED_PART: [
        PREFABRICATED_PART_ASSEMBLE,
        REINFORCE,
        POUR_CONCRETE,
        PART_COMPLETE,
    ],
    MASONRY: [DO_MASONRY, PART_COMPLETE],
}

working_steps_flat = set(
    item
    for sublist in [working_steps[key] for key in working_steps]
    for item in sublist
)

color_map_for_plotly = {
    step: "rgb" + str(all_colors[step]) for step in working_steps_flat
}
