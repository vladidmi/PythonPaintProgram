from utils import *

WIN = pygame.display.set_mode((WIDTH, HEIGHT+TOOLBAR_HEIGHT))
pygame.display.set_caption("Wochenprogramm")

def init_grid(rows, cols):
    grid = [[Pixel(i,j) for i in range(cols)] for j in range(rows)]
    return grid

def draw_grid(win, grid, current_mode):
    for i, row in enumerate(grid): 
        for j, pixel in enumerate(row):
            current_color_key, current_transparency = pixel.get_color_key(current_mode, current_day)
            if current_color_key:
                pixel.draw_color(win,current_color_key,current_transparency,i,j)
                
def draw_buttons(win, current_mode):
    for i,current_button in enumerate(DRAWING_MODES[current_mode]):
        button = DRAWING_MODES[current_mode][current_button]
        button.x = 10 * (1+i) + i * BOX_SIZE 
        button.draw(win)

    pygame.display.update()

def get_row_col_from_pos(pos):
    x, y = pos
    row = y // PIXEL_SIZE
    col = x // PIXEL_SIZE

    if row >= ROWS:
        raise IndexError
    return row, col

def tact_deleted(grid, number_of_tacts):
    for i, row in enumerate(grid):
        for j, pixel in enumerate(row):
            if pixel.tact == number_of_tacts:
                pixel.tact = None
                pixel.color = None

run = True
clock = pygame.time.Clock()
grid = init_grid(ROWS, COLS)
drawing_color = BLACK
drawing_mode_id = 0
current_tact = None
current_structure = None
current_status = None

current_day = pd.Timestamp(datetime.date.today())

while run:
    current_mode = list(DRAWING_MODES)[drawing_mode_id]

    WIN.fill(BG_COLOR)
    clock.tick(FPS)
    
    #Background image
    WIN.blit(img, img_rect)
    #Date with day name
    today_string = current_day.strftime("%A-%d-%m-%Y")
    for german_week_day in GERMAN_WEEK_DAYS:
        today_string = today_string.replace(*german_week_day)
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
                        curren_pixel = grid[current_pixel_y][curren_pixel_x]
                        
                        if not (0<=curren_pixel_x<COLS and 0<=current_pixel_y<ROWS):
                            continue
                        elif current_mode == PLAN and \
                            DRAWING_COLOR_ORDER[DRAWING_COLOR_ORDER.index(
                                curren_pixel.color
                                )+1] == drawing_color:
                            curren_pixel.color = drawing_color
                            try:
                                curren_pixel.status[current_status].append(current_day)
                            except KeyError as e:
                                print(curren_pixel.status)

                        elif current_mode == DRAW_SCTRUCTURE and current_structure:
                            curren_pixel.color = drawing_color
                            curren_pixel.type_structure = current_structure

                            for step in working_steps[current_structure]:
                                curren_pixel.status[step] = list()

                        elif current_mode == TACT:
                            curren_pixel.tact = tact_id
            except IndexError:
                for current_button in DRAWING_MODES[current_mode]:
                    try:
                        button = DRAWING_MODES[current_mode][current_button]
                    except KeyError as e:
                        e
                    if not button.clicked(pos, current_mode):
                        continue
                    
                    if button.text == CLEAR:
                        grid = init_grid(ROWS, COLS)
                        drawing_color = BLACK
                    elif button.text == BIGGER:
                        pixel_size_increase+=1
                    elif button.text == SMALLER:
                        pixel_size_increase=max(1,pixel_size_increase-1)
                    elif button.text == NEXT_DAY:
                        current_day+=1*german_business_day
                    elif button.text == LAST_DAY:
                        current_day-=1*german_business_day
                    elif button.text == DRAW_MODE:
                        drawing_mode_id = (drawing_mode_id+1)%len(DRAWING_MODES)
                        current_structure = None
                        current_tact = None
                        drawing_color = None
                        current_status= None
                    elif button.text == tact_add and number_of_tacts<6:
                        number_of_tacts+=1
                        temp_tact = f'{TACT_PART} {number_of_tacts}'
                        tact_buttons[temp_tact] = Button(y=button_y, width=BOX_SIZE, height=BOX_SIZE, color=all_colors[temp_tact], text = temp_tact, label = temp_tact)
                        DRAWING_MODES[TACT] = {**common_buttons, **tact_button_options, **tact_buttons}
                    elif button.text == tact_delete and number_of_tacts>2:
                        tact_deleted(grid, number_of_tacts)
                        del (tact_buttons[list(tact_buttons)[-1]])
                        DRAWING_MODES[TACT] = {**common_buttons, **tact_button_options, **tact_buttons}
                        number_of_tacts-=1
                    elif TACT_PART in button.text:
                        tact_id = button.text
                        drawing_color = all_colors[button.text]
                    elif current_mode == DRAW_SCTRUCTURE and button.text in draw_structure_buttons:
                        current_structure = button.text
                        drawing_color = button.color
                    elif current_mode == PLAN and button.text in plan_buttons:
                        current_status = button.text
                        drawing_color = button.color
                    else:
                        drawing_color = button.color         
    draw_grid(WIN, grid, current_mode)
    draw_buttons(WIN, current_mode)
    
pygame.quit()
