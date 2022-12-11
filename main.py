from utils import *

WIN = pygame.display.set_mode((WIDTH, HEIGHT+TOOLBAR_HEIGHT))
pygame.display.set_caption("Wochenprogramm")

def init_grid(rows, cols, color):
    grid = [[Pixel(i,j,color) for i in range(cols)] for j in range(rows)]
    return grid

def draw_grid(win, grid):
    for i, row in enumerate(grid):
        for j, pixel in enumerate(row):
            if pixel.color!=WHITE:
                #drawing with transparency (https://stackoverflow.com/questions/6339057/draw-a-transparent-rectangles-and-polygons-in-pygamepyg)
                s = pygame.Surface((PIXEL_SIZE,PIXEL_SIZE)) # the size of the rect
                s.set_alpha(int(TRANSPARENCY*256)) # alpha level
                s.fill(pixel.color) # this fills the entire surface
                win.blit(s, (j * PIXEL_SIZE,i *
                                            PIXEL_SIZE)) # the top-left coordinates
                
def draw(win, grid, buttons):
    draw_grid(win, grid)

    for current_button in DRAWING_MODES[list(DRAWING_MODES)[drawing_mode_id]]:
        button = buttons[current_button]
        button.draw(win)

    pygame.display.update()

def get_row_col_from_pos(pos):
    x, y = pos
    row = y // PIXEL_SIZE
    col = x // PIXEL_SIZE

    if row >= ROWS:
        raise IndexError

    return row, col

run = True
clock = pygame.time.Clock()
grid = init_grid(ROWS, COLS, BG_COLOR)
drawing_color = BLACK
drawing_mode_id = 0

button_y = HEIGHT + BOX_SIZE//2

buttons = {
    'Black':Button(10, button_y, BOX_SIZE, BOX_SIZE, BLACK),
    'Red':Button(70, button_y, BOX_SIZE, BOX_SIZE, RED),
    'Green':Button(130, button_y, BOX_SIZE, BOX_SIZE, GREEN),
    'Blue':Button(190, button_y, BOX_SIZE, BOX_SIZE, BLUE),
    'Erase':Button(250, button_y, BOX_SIZE, BOX_SIZE, WHITE, "Erase", BLACK),
    'Clear':Button(310, button_y, BOX_SIZE, BOX_SIZE, WHITE, "Clear", BLACK),
    'Bigger':Button(370, button_y, BOX_SIZE, BOX_SIZE, WHITE, "Bigger", BLACK),
    'Smaller':Button(430, button_y, BOX_SIZE, BOX_SIZE, WHITE, "Smaller", BLACK),
    'Last day':Button(490, button_y, BOX_SIZE, BOX_SIZE, WHITE, "Last day", BLACK),
    'Next day':Button(550, button_y, BOX_SIZE, BOX_SIZE, WHITE, "Next day", BLACK),
    'Draw mode':Button(610, button_y, BOX_SIZE, BOX_SIZE, WHITE, "Draw mode", BLACK),
}

today = datetime.date.today()

while run:

    WIN.fill(BG_COLOR)
    clock.tick(FPS)
    
    #Background image
    WIN.blit(img, img_rect)
    #Date with day name
    today_string = today.strftime("%A-%d-%m-%Y")
    text_surface = get_font(22).render(today_string, 1, BLACK)
    WIN.blit(text_surface, (10,10))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

        if pygame.mouse.get_pressed()[0]:
            pos = pygame.mouse.get_pos()
            try:
                row, col = get_row_col_from_pos(pos)
                for pixel_width in range(pixel_size_increase):
                    for pixel_height in range(pixel_size_increase):

                        curren_pixel_x = pixel_width+col-pixel_size_increase//2
                        current_pixel_y = pixel_height+row-pixel_size_increase//2
                        
                        if 0<=curren_pixel_x<COLS and 0<=current_pixel_y<ROWS and \
                            DRAWING_COLOR_ORDER[DRAWING_COLOR_ORDER.index(
                                grid[current_pixel_y][curren_pixel_x].color
                                )+1] == drawing_color and drawing_color!=WHITE:
                            grid[current_pixel_y][curren_pixel_x].color = drawing_color
            except IndexError:
                for current_button in buttons:
                    button = buttons[current_button]
                    if not button.clicked(pos):
                        continue
                    
                    if button.text == "Clear":
                        grid = init_grid(ROWS, COLS, BG_COLOR)
                        drawing_color = BLACK
                    elif button.text == "Bigger":
                        pixel_size_increase+=1
                    elif button.text == "Smaller":
                        pixel_size_increase=max(1,pixel_size_increase-1)
                    elif button.text == "Next day":
                        today+=1*german_business_day
                    elif button.text == "Last day":
                        today-=1*german_business_day
                    elif button.text == "Draw mode":
                        drawing_mode_id = (drawing_mode_id+1)%2
                    else:
                        drawing_color = button.color         

    draw(WIN, grid, buttons)
    
pygame.quit()
