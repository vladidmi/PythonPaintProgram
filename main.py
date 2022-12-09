from utils import *

WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Drawing Program")


def init_grid(rows, cols, color):
    grid = []

    for i in range(rows):
        grid.append([])
        for _ in range(cols):
            grid[i].append(color)

    return grid


def draw_grid(win, grid):
    for i, row in enumerate(grid):
        for j, pixel in enumerate(row):
            if pixel!=WHITE:
                #drawing with transparency (https://stackoverflow.com/questions/6339057/draw-a-transparent-rectangles-and-polygons-in-pygamepyg)
                s = pygame.Surface((PIXEL_SIZE,PIXEL_SIZE)) # the size of your rect
                s.set_alpha(128) # alpha level
                s.fill(pixel) # this fills the entire surface
                win.blit(s, (j * PIXEL_SIZE,i *
                                            PIXEL_SIZE)) # the top-left coordinates
                
                #drawing without transparency
                # pygame.draw.rect(win, pixel, (j * PIXEL_SIZE, i *
                #                             PIXEL_SIZE, PIXEL_SIZE, PIXEL_SIZE))

    if DRAW_GRID_LINES:
        for i in range(ROWS + 1):
            pygame.draw.line(win, BLACK, (0, i * PIXEL_SIZE),
                             (WIDTH, i * PIXEL_SIZE))

        for i in range(COLS + 1):
            pygame.draw.line(win, BLACK, (i * PIXEL_SIZE, 0),
                             (i * PIXEL_SIZE, HEIGHT - TOOLBAR_HEIGHT))


def draw(win, grid, buttons):
    draw_grid(win, grid)

    for button in buttons:
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

button_y = HEIGHT - TOOLBAR_HEIGHT/2 - 25
buttons = [
    Button(10, button_y, 50, 50, BLACK),
    Button(70, button_y, 50, 50, RED),
    Button(130, button_y, 50, 50, GREEN),
    Button(190, button_y, 50, 50, BLUE),
    Button(250, button_y, 50, 50, WHITE, "Erase", BLACK),
    Button(310, button_y, 50, 50, WHITE, "Clear", BLACK),
    Button(370, button_y, 50, 50, WHITE, "Bigger", BLACK),
    Button(430, button_y, 50, 50, WHITE, "Smaller", BLACK),
    Button(490, button_y, 50, 50, WHITE, "Last", BLACK),
    Button(550, button_y, 50, 50, WHITE, "Next", BLACK),
]

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
                        
                        if 0<=curren_pixel_x<ROWS and 0<=current_pixel_y<ROWS and \
                            DRAWING_COLOR_ORDER[DRAWING_COLOR_ORDER.index(
                                grid[current_pixel_y][curren_pixel_x]
                                )+1]==drawing_color and drawing_color!=WHITE:
                            grid[current_pixel_y][curren_pixel_x] = drawing_color
            except IndexError:
                for button in buttons:
                    if not button.clicked(pos):
                        continue
                    
                    if button.text == "Clear":
                        grid = init_grid(ROWS, COLS, BG_COLOR)
                        drawing_color = BLACK
                    elif button.text == "Bigger":
                        pixel_size_increase+=1
                    elif button.text == "Smaller":
                        pixel_size_increase=max(1,pixel_size_increase-1)
                    elif button.text == "Next":
                        today+=1*german_business_day
                    elif button.text == "Last":
                        today-=1*german_business_day    
                    else:
                        drawing_color = button.color         

    draw(WIN, grid, buttons)
    
pygame.quit()
