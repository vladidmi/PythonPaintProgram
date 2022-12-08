import pygame
import os

cur_dir = os.getcwd()

image_path = os.path.join(cur_dir,'utils','imgs','grundriss.jpg')
img = pygame.image.load(image_path)
#img.convert()
img_rect = img.get_rect()

pygame.init()
pygame.font.init()

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
