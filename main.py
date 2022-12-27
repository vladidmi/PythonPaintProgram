from utils import *

WIN = pygame.display.set_mode((WIDTH, HEIGHT + TOOLBAR_HEIGHT))
pygame.display.set_caption(f"Wochenprogramm")


def init_grid(rows, cols, pixel_history):
    grid = list()
    for j in range(rows):
        grid.append(list())
        for i in range(cols):
            if f"{i}-{j}" not in pixel_history:
                grid[j].append(Pixel(i, j))
            else:
                type_structure = pixel_history[f"{i}-{j}"]["pixel_type_structure"]
                status = dict()
                if type_structure:
                    for step in working_steps[type_structure]:
                        current_step = pixel_history[f"{i}-{j}"].get(step, set())
                        status[step] = current_step
                grid[j].append(
                    Pixel(
                        pixel_x=i,
                        pixel_y=j,
                        tact=pixel_history[f"{i}-{j}"]["pixel_BA"],
                        type_structure=type_structure,
                        status=status,
                    )
                )
    # work in porgress                number_of_tacts = max(2, int(pixel_history[f'{i}-{j}']['pixel_BA'].split()[-1]))
    return grid


def draw_grid(win, grid, current_mode):
    for i, row in enumerate(grid):
        for j, pixel in enumerate(row):
            current_color_key, current_transparency = pixel.get_color_key(
                current_mode, current_day
            )
            if current_color_key:
                pixel.draw_color(win, current_color_key, current_transparency, i, j)


def draw_buttons(win, current_mode):
    for i, current_button in enumerate(DRAWING_MODES[current_mode]):
        button = DRAWING_MODES[current_mode][current_button]
        button.x = 10 * (1 + i) + i * BOX_SIZE
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


def save_pixel_info(all_floor_level_info, make_time_plan=False):
    all_floor_levels = list()
    for temp_floor in all_floor_level_info:
        grid = temp_floor.grid
        pixel_info = list()
        for i, row in enumerate(grid):
            for j, pixel in enumerate(row):
                if pixel.tact or pixel.type_structure:
                    pixel_info.append(
                        {
                            "pixel_id": f"{pixel.pixel_x}-{pixel.pixel_y}",
                            "pixel_x": pixel.pixel_x,
                            "pixel_y": pixel.pixel_y,
                            "pixel_type_structure": pixel.type_structure,
                            "pixel_BA": pixel.tact,
                            **pixel.status,
                        }
                    )
        df = pd.DataFrame(pixel_info)
        df.to_excel(temp_floor.full_path_xlsx, index=False)

        if make_time_plan:
            df["geschoss"] = temp_floor.floor_name
            for df_column in df.columns:
                if df_column in working_steps_flat:
                    df[f"{df_column}_erster_Tag"] = df[df_column].apply(
                        return_only_from_set, function_for_set=min
                    )
                    df[f"{df_column}_letzter_Tag"] = df[df_column].apply(
                        return_only_from_set, function_for_set=max
                    )
            all_floor_levels.append(df)

    if make_time_plan:
        all_floor_levels_df = pd.concat(all_floor_levels)
        floor_levels_df_grouped = (
            all_floor_levels_df.groupby(
                ["geschoss", "pixel_BA", "pixel_type_structure"]
            )
            .agg([min, max])
            .reset_index()
        )

        floor_levels_df_grouped.to_excel(
            os.path.join(path_to_image_folder, "zeitplan.xlsx")
        )


def load_pixel_info(pixel_info_file):
    def get_dates(str_list):
        return set(
            pd.Timestamp(date)
            for date in re.findall(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}", str_list)
        )

    df = pd.read_excel(pixel_info_file, index_col=0)
    df = df.replace({np.nan: None})
    pixel_dict = df.to_dict("index")
    for key, pixel_id in pixel_dict.items():
        for key1, pixel_attribute in pixel_id.items():
            if type(pixel_attribute) == str and "Timestamp" in pixel_attribute:
                pixel_dict[key][key1] = get_dates(pixel_attribute)
            elif type(pixel_attribute) == str and "set()" in pixel_attribute:
                pixel_dict[key][key1] = set()
    return pixel_dict


def return_only_from_set(value, function_for_set):
    if type(value) == set and value:
        return function_for_set(value)
    else:
        return None


run = True
clock = pygame.time.Clock()

all_floor_level_info = list()
for image_file in full_image_path:
    new_floor_level = Floor_level_info(image_file, full_image_path[image_file])
    try:
        pixel_history = load_pixel_info(new_floor_level.full_path_xlsx)
    except FileNotFoundError as e:
        pixel_history = dict()
        print("File not found")
    new_floor_level.grid = init_grid(ROWS, COLS, pixel_history)
    all_floor_level_info.append(new_floor_level)

drawing_mode_id = 0
current_tact = None
current_structure = None
current_status = None
current_floor_id = 0

current_day = pd.Timestamp(datetime.date.today())

while run:
    current_mode = list(DRAWING_MODES)[drawing_mode_id]
    current_floor = all_floor_level_info[current_floor_id]
    current_image = current_floor.full_path_image
    grid = current_floor.grid

    WIN.fill(BG_COLOR)
    clock.tick(FPS)

    # Background image
    img = pygame.image.load(current_image)
    img_rect = img.get_rect(
        topleft=(
            (WIDTH - current_floor.image_width) // 2,
            (HEIGHT - current_floor.image_height) // 2,
        )
    )
    WIN.blit(img, img_rect)

    # Showing date with day name
    today_string = current_day.strftime("%A-%d-%m-%Y")
    for german_week_day in GERMAN_WEEK_DAYS:
        today_string = today_string.replace(*german_week_day)
    text_surface = get_font(22).render(today_string, 1, BLACK)
    WIN.blit(text_surface, (10, 10))

    # Showing current floor name
    text_surface = get_font(22).render(current_floor.floor_name, 1, BLACK)
    WIN.blit(text_surface, (900, 10))

    for event in pygame.event.get():
        if (
            event.type == pygame.QUIT
            or event.type == pygame.KEYDOWN
            and event.key == pygame.K_ESCAPE
        ):
            save_pixel_info(all_floor_level_info, make_time_plan=True)
            run = False

        if pygame.mouse.get_pressed()[0]:
            pos = pygame.mouse.get_pos()
            try:
                row, col = get_row_col_from_pos(pos)
                for pixel_width in range(pixel_size_increase):
                    for pixel_height in range(pixel_size_increase):

                        curren_pixel_x = pixel_width + col - pixel_size_increase // 2
                        current_pixel_y = pixel_height + row - pixel_size_increase // 2
                        current_pixel = grid[current_pixel_y][curren_pixel_x]

                        if not (
                            0 <= curren_pixel_x < COLS and 0 <= current_pixel_y < ROWS
                        ):
                            continue
                        elif (
                            current_mode == PLAN
                            and current_status
                            in working_steps.get(current_pixel.type_structure, [])
                        ):
                            try:
                                current_pixel.status[current_status].add(current_day)
                            except KeyError as e:
                                print("Problem with status", current_pixel)

                        elif current_mode == DRAW_SCTRUCTURE and current_structure:
                            current_pixel.type_structure = current_structure

                            for step in working_steps[current_structure]:
                                current_pixel.status[step] = set()

                        elif current_mode == TACT:
                            current_pixel.tact = tact_id
            except IndexError:
                for current_button in DRAWING_MODES[current_mode]:
                    try:
                        button = DRAWING_MODES[current_mode][current_button]
                    except KeyError as e:
                        e
                    if not button.clicked(pos, current_mode):
                        continue

                    if button.text == CLEAR:
                        # should be implemented
                        pass
                    elif button.text == NEXT_FLOOR:
                        current_floor_id = (current_floor_id + 1) % len(full_image_path)
                        button_sleep()
                    elif button.text == PREVIOUS_FLOOR:
                        current_floor_id = (
                            current_floor_id - 1 + len(full_image_path)
                        ) % len(full_image_path)
                        button_sleep()
                    elif button.text == BIGGER:
                        pixel_size_increase += 1
                    elif button.text == SMALLER:
                        pixel_size_increase = max(1, pixel_size_increase - 1)
                    elif button.text == NEXT_DAY:
                        current_day += 1 * german_business_day
                        button_sleep()
                    elif button.text == LAST_DAY:
                        current_day -= 1 * german_business_day
                        button_sleep()
                    elif button.text == DRAW_MODE:
                        drawing_mode_id = (drawing_mode_id + 1) % len(DRAWING_MODES)
                        current_structure = None
                        current_tact = None
                        current_status = None
                        button_sleep()
                    elif button.text == tact_add and number_of_tacts < 6:
                        number_of_tacts += 1
                        temp_tact = f"{TACT_PART} {number_of_tacts}"
                        tact_buttons[temp_tact] = Button(
                            y=button_y,
                            width=BOX_SIZE,
                            height=BOX_SIZE,
                            color=all_colors[temp_tact],
                            text=temp_tact,
                            label=temp_tact,
                        )
                        DRAWING_MODES[TACT] = {
                            **common_buttons,
                            **tact_button_options,
                            **tact_buttons,
                        }
                        button_sleep()
                    elif button.text == tact_delete and number_of_tacts > 2:
                        tact_deleted(grid, number_of_tacts)
                        del tact_buttons[list(tact_buttons)[-1]]
                        DRAWING_MODES[TACT] = {
                            **common_buttons,
                            **tact_button_options,
                            **tact_buttons,
                        }
                        number_of_tacts -= 1
                        button_sleep()
                    elif TACT_PART in button.text:
                        tact_id = button.text
                    elif (
                        current_mode == DRAW_SCTRUCTURE
                        and button.text in draw_structure_buttons
                    ):
                        current_structure = button.text
                    elif current_mode == PLAN and button.text in plan_buttons:
                        current_status = button.text

    draw_grid(WIN, grid, current_mode)
    draw_buttons(WIN, current_mode)
    clock.tick()
    pygame.display.set_caption(f"Wochenprogramm running at {int(clock.get_fps())} FPS")

pygame.quit()
