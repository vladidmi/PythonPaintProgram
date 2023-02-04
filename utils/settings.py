import os
import datetime
import holidays
from pandas.tseries.offsets import CustomBusinessDay
from PIL import Image, ImageDraw, ImageFont
import pandas as pd
import re
import numpy as np
import time
import plotly.express as px


def resize_image(image_path):
    # resizing the image to fit into the given rectangular
    image = Image.open(image_path)
    current_image_width, current_image_height = image.size
    resize_ratio = min(WIDTH / current_image_width, HEIGHT / current_image_height)
    new_image_width = int(current_image_width * resize_ratio)
    new_image_height = int(current_image_height * resize_ratio)
    image_resized = image.resize((new_image_width, new_image_height))
    blank_image = Image.new(mode="RGB", size=(WIDTH, HEIGHT), color=WHITE)
    offset = ((WIDTH - new_image_width) // 2, (HEIGHT - new_image_height) // 2)
    blank_image.paste(image_resized, offset)
    blank_image.save(image_path)


def weekdays_of_current_week(current_date):
    current_date = list(current_date.isocalendar())

    weekdays = []
    for i in range(1, 6):
        current_date[2] = i
        current_date_iso = datetime.datetime.fromisocalendar(*current_date).date()
        if current_date_iso not in german_holidays:
            weekdays.append(current_date_iso)

    return weekdays


class Floor_level_info:
    def __init__(self, image_name, full_image_name):
        self.image_name = image_name
        self.full_path_image = full_image_name
        self.full_path_xlsx = full_image_name.replace("jpg", "xlsx")
        self.floor_name = image_name.replace(".jpg", "")

        try:
            self.image = Image.open(self.full_path_image)
            self.image_width, self.image_height = self.image.size
        except FileNotFoundError:
            self.image_width, self.image_height = WIDTH, HEIGHT


cur_dir = os.getcwd()

WIDTH, HEIGHT = 1200, 750

PIXEL_SIZE = 7

ROWS = HEIGHT // PIXEL_SIZE
COLS = WIDTH // PIXEL_SIZE

BUTTON_TEXT_SIZE = 12
PROJECT_INFO_TEXT_SIZE = 22

project_font_path = ImageFont.truetype(
    os.path.join(cur_dir, "utils", "arial.ttf"), PROJECT_INFO_TEXT_SIZE
)
project_font_path_small = ImageFont.truetype(
    os.path.join(cur_dir, "utils", "arial.ttf"), BUTTON_TEXT_SIZE
)

path_to_image_folder = os.path.join(cur_dir, "imgs")
full_image_path = {
    file: os.path.join(path_to_image_folder, file)
    for file in os.listdir(path_to_image_folder)
    if ".jpg" in file
}

weekmask_germany = "Mon Tue Wed Thu Fri"
german_holidays = [
    date[0]
    for date in holidays.Germany(years=list(range(2020, 2040)), prov="BW").items()
]

for year in range(2020, 2030):
    # adding the winter pause (CW52,CW1)
    for week in [52, 1]:
        for day in range(7):
            week1 = f"{year}-W{week}"
            day1 = datetime.datetime.strptime(
                week1 + "-1", "%Y-W%W-%w"
            ) + datetime.timedelta(days=day)
            german_holidays.append(day1)

german_business_day = CustomBusinessDay(
    holidays=german_holidays, weekmask=weekmask_germany
)

WHITE = "#ffffff"
BLACK = "#000000"
RED = "#ff0000"
BLUE = "#0000ff"
GREEN = "#00ff00"
YELLOW = "#ffff00"  # Schalen
LIGHT_BLUE = "#00b0f0"  # Bewehren
LIGHT_GREEN = "#00c000"  # Betonieren
VIOLET = "#8057ff"  # Fertigteil setzen
ORANGE = "#ffc000"  # Mauern
DARK_RED = "#c00000"  # Fertig
GREY = "#808080"
BROWN = "#a52a2a"

BG_COLOR = WHITE
TRANSPARENT = 0.2
SEMI_TRANSPARENT = 0.75
NOT_TRANSPARENT = 1

pixel_size_increase = 2

GERMAN_WEEK_DAYS = (
    ("Monday", "Montag"),
    ("Tuesday", "Dienstag"),
    ("Wednesday", "Mittwoch"),
    ("Thursday", "Donnerstag"),
    ("Friday", "Freitag"),
    ("Saturday", "Samstag"),
    ("Sunday", "Sonntag"),
)

HORIZONTAL = "horizontal"
VERTICAL = "vertical"
CURSOR_SIZE = "Kursorgröße"

# COMMON
ERASE = "Entf."
SAVE = "Speichern"
BIGGER = "Größer"
SMALLER = "Kleiner"
DRAW_MODE = "Modus"
NEXT_FLOOR = "Ebene +"
PREVIOUS_FLOOR = "Ebene -"
PRINT = "Drucken"
BUTTON_COLOUR = "Button_colour"
BUTTON_TEXT_COLOUR = "Button_text_colour"

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
    PRINT: WHITE,
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
    NEXT_DAY: WHITE,
    LAST_DAY: WHITE,
    # Tact division
    f"{TACT_PART} 1": BLUE,
    f"{TACT_PART} 2": ORANGE,
    f"{TACT_PART} 3": VIOLET,
    f"{TACT_PART} 4": GREY,
    f"{TACT_PART} 5": YELLOW,
    f"{TACT_PART} 6": BROWN,
    NO_TACT: WHITE,
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
