import pygame
import os
import datetime
import holidays
from pandas.tseries.offsets import CustomBusinessDay
from PIL import Image

cur_dir = os.getcwd()

WIDTH, HEIGHT = 1000, 700

image_path = os.path.join(cur_dir,'utils','imgs','grundriss.jpg') 
#resizing the image to fit into rect 1000x700
image = Image.open(image_path)
current_image_width, current_image_height = image.size
resize_ratio = min(WIDTH/current_image_width, HEIGHT/current_image_height)
new_image_size = (int(current_image_width * resize_ratio), 
                    int(current_image_height * resize_ratio))
image_resized = image.resize(new_image_size)
resized_image_path = image_path.replace('grundriss.jpg','grundriss_resized.jpg')
image_resized.save(resized_image_path)

img = pygame.image.load(resized_image_path)
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

PIXEL_SIZE = 3

ROWS = HEIGHT//PIXEL_SIZE
COLS = WIDTH//PIXEL_SIZE

BOX_SIZE = 50
TOOLBAR_HEIGHT = 2* BOX_SIZE

BG_COLOR = WHITE
TRANSPARENCY = 0.2

DRAW_GRID_LINES = False

pixel_size_increase = 3

DRAWING_COLOR_ORDER = [WHITE, BLACK, RED, GREEN, BLUE, WHITE]

def get_font(size):
    return pygame.font.SysFont("comicsans", size)
