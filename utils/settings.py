import pygame
import os
import datetime
import holidays
from pandas.tseries.offsets import CustomBusinessDay
from PIL import Image, ImageDraw
import pandas as pd
import re
import numpy as np
import time
import plotly.express as px


def button_sleep(seconds_to_sleep=0.2):
    time.sleep(seconds_to_sleep)


def resize_image(image_path):
    # resizing the image to fit into rect 1000x700
    image = Image.open(image_path)
    current_image_width, current_image_height = image.size
    resize_ratio = min(WIDTH / current_image_width, HEIGHT / current_image_height)
    new_image_width = int(current_image_width * resize_ratio)
    new_image_height = int(current_image_height * resize_ratio)
    image_resized = image.resize((new_image_width, new_image_height))
    resized_image_path = image_path.replace(".jpg", "_resized.jpg")
    image_resized.save(resized_image_path)
    return resized_image_path, new_image_width, new_image_height


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

path_to_image_folder = os.path.join(cur_dir, "utils", "imgs")
full_image_path = {
    file: os.path.join(path_to_image_folder, file)
    for file in os.listdir(path_to_image_folder)
    if ".jpg" in file
}

pygame.init()
pygame.font.init()

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

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)  # Schalen
LIGHT_BLUE = (0, 176, 240)  # Bewehren
LIGHT_GREEN = (0, 192, 0)  # Betonieren
VIOLET = (128, 87, 255)  # Fertigteil setzen
ORANGE = (255, 192, 0)  # Mauern
DARK_RED = (192, 0, 0)  # Fertig
GREY = (128, 128, 128)
BROWN = (165, 42, 42)

FPS = 100

PIXEL_SIZE = 7

ROWS = HEIGHT // PIXEL_SIZE
COLS = WIDTH // PIXEL_SIZE

BOX_SIZE = 50
TOOLBAR_HEIGHT = TOOLBAR_WIDTH = 2 * BOX_SIZE


BG_COLOR = WHITE
TRANSPARENT = 0.2
SEMI_TRANSPARENT = 0.75
NOT_TRANSPARENT = 1

pixel_size_increase = 2


def get_font(size):
    return pygame.font.SysFont("comicsans", size)


GERMAN_WEEK_DAYS = (
    ("Monday", "Montag"),
    ("Tuesday", "Diesntag"),
    ("Wednesday", "Mittwoch"),
    ("Thursday", "Donnerstag"),
    ("Friday", "Freitag"),
    ("Saturday", "Samstag"),
    ("Sunday", "Sonntag"),
)

HORIZONTAL = "horizontal"
VERTICAL = "vertical"
