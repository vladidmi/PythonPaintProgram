import pygame
import os
import datetime
import holidays
from pandas.tseries.offsets import CustomBusinessDay

cur_dir = os.getcwd()

image_path = os.path.join(cur_dir,'utils','imgs','grundriss.jpg')
img = pygame.image.load(image_path)
#img.convert()
img_rect = img.get_rect()

pygame.init()
pygame.font.init()

weekmask_ger = 'Mon Tue Wed Thu Fri'
german_holidays=[date[0] for date in holidays.Germany(years=list(range(2020,2040)),prov='BW').items()]
for year in range(2020,2030):
# adding the summer pause (CW 33,34) and the winter pause (CW52,CW1)
    for week in [52,1]:
        for day in range(7):
            week1 = f"{year}-W{week}"
            day1 = datetime.datetime.strptime(week1 + '-1', "%Y-W%W-%w")+datetime.timedelta(days=day)
            german_holidays.append(day1)

german_business_day = CustomBusinessDay(holidays=german_holidays, weekmask=weekmask_ger)

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 255, 0)
GREEN = (0, 0, 255)

FPS = 240

WIDTH, HEIGHT = 600, 700

ROWS = COLS = 200

TOOLBAR_HEIGHT = HEIGHT - WIDTH

PIXEL_SIZE = WIDTH // COLS

BG_COLOR = WHITE

DRAW_GRID_LINES = False

pixel_size_increase = 5

DRAWING_COLOR_ORDER = [WHITE, BLACK, RED, GREEN, BLUE, WHITE]

def get_font(size):
    return pygame.font.SysFont("comicsans", size)
