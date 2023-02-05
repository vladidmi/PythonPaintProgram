from utils import *

while run:
    current_mode = list(DRAWING_MODES)[drawing_mode_id]
    current_floor = all_floor_level_info[current_floor_id]
    current_image = current_floor.full_path_image
    grid = current_floor.grid

    WIN.fill(BG_COLOR)
    clock.tick(FPS)

    # Showing date with day name
    today_string = current_day.strftime("%A-%d-%m-%Y")
    for german_week_day in GERMAN_WEEK_DAYS:
        today_string = today_string.replace(*german_week_day)
    text_surface = get_font(PROJECT_INFO_TEXT_SIZE).render(today_string, 1, BLACK)
    WIN.blit(text_surface, (10, 10))

    # Showing current floor name
    text_surface = get_font(PROJECT_INFO_TEXT_SIZE).render(
        current_floor.floor_name, 1, BLACK
    )
    WIN.blit(text_surface, (600, 10))

    # Showing current cursor size
    cursor_text_size_surface = get_font(PROJECT_INFO_TEXT_SIZE).render(
        CURSOR_SIZE, 1, BLACK
    )
    WIN.blit(cursor_text_size_surface, (WIDTH - BOX_SIZE // 2, HEIGHT - BOX_SIZE // 2))

    # Drawing cursor
    for pixel_width in range(pixel_size_increase):
        for pixel_height in range(pixel_size_increase):
            Pixel.draw_color(
                win=WIN,
                current_color_key=CONCRETE,
                transparency_level=NOT_TRANSPARENT,
                i=ROWS + pixel_height,
                j=COLS + pixel_width,
            )

    for event in pygame.event.get():
        if (
            event.type == pygame.QUIT
            or event.type == pygame.KEYDOWN
            and event.key == pygame.K_ESCAPE
        ):
            save_pixel_info(all_floor_level_info, make_time_plan=True)
            run = False

        if event.type == pygame.KEYUP and event.key == pygame.K_LSHIFT:
            shift_x = None
            shift_y = None
            drawing_direction = None

        if pygame.mouse.get_pressed()[0]:
            pos = pygame.mouse.get_pos()
            x, y = pos

            pressed_keys = pygame.key.get_pressed()
            if pressed_keys[pygame.K_LSHIFT]:
                if not shift_x and not shift_y:
                    shift_x, shift_y = pos
                if not drawing_direction:
                    if shift_x < x or shift_x > x:
                        drawing_direction = HORIZONTAL
                    elif shift_y < y or shift_y > y:
                        drawing_direction = VERTICAL
                if drawing_direction == HORIZONTAL:
                    y = shift_y
                elif drawing_direction == VERTICAL:
                    x = shift_x
                pos = x, y

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

                        # Draw mode
                        elif current_mode == DRAW_SCTRUCTURE:
                            if erase_mode == True:
                                current_pixel.type_structure = None
                                current_pixel.status = dict()
                            elif current_structure:
                                current_pixel.type_structure = current_structure
                                current_pixel.status = dict()
                                for step in working_steps[current_structure]:
                                    current_pixel.status[step] = set()

                        # Tact mode
                        elif current_mode == TACT:
                            if erase_mode == True:
                                current_pixel.tact = None
                            else:
                                current_pixel.tact = tact_id

                        # Plan mode
                        elif current_mode == PLAN:
                            if erase_mode == True:
                                for step in current_pixel.status:
                                    current_pixel.status[step].discard(current_day)
                            elif current_status in working_steps.get(
                                current_pixel.type_structure, []
                            ):
                                try:
                                    if active_tact_for_planing == current_pixel.tact:
                                        current_pixel.status[current_status].add(
                                            current_day
                                        )
                                except KeyError as e:
                                    print("Problem with status", current_pixel)

            except IndexError:
                for current_button in {**common_buttons, **DRAWING_MODES[current_mode]}:
                    try:
                        button = {**common_buttons, **DRAWING_MODES[current_mode]}[
                            current_button
                        ]
                    except KeyError as e:
                        e
                    if not button.clicked(pos, current_mode):
                        continue

                    print(f"Button {button.text} clicked")

                    if button.text != ERASE and button.text != NO_TACT:
                        erase_mode = False
                    if button.text == SAVE:
                        save_pixel_info(all_floor_level_info, make_time_plan=True)
                    elif (
                        button.text == ERASE
                        or current_mode == TACT
                        and button.text == NO_TACT
                    ):
                        erase_mode = True
                    elif button.text == NEXT_FLOOR:
                        current_floor_id = (current_floor_id + 1) % len(full_image_path)
                        button_sleep()
                    elif button.text == PREVIOUS_FLOOR:
                        current_floor_id = (
                            current_floor_id - 1 + len(full_image_path)
                        ) % len(full_image_path)
                        button_sleep()
                    elif button.text == BIGGER:
                        pixel_size_increase = min(14, pixel_size_increase + 1)
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
                        active_tact_for_planing = f"{TACT_PART} 1"
                        button_sleep()
                    elif button.text == PRINT:
                        weekdays_to_print = weekdays_of_current_week(current_day)

                        for floor in all_floor_level_info:
                            folder_with_floor = floor.full_path_image.replace(
                                floor.image_name, ""
                            )
                            floor.folder_with_print = os.path.join(
                                folder_with_floor, "output", floor.floor_name
                            )
                            try:
                                os.mkdir(floor.folder_with_print)
                            except OSError as e:
                                e
                            for weekday in weekdays_to_print:
                                draw_grid_for_print(floor, weekday)
                        print("all images created")
                        button_sleep()
                    elif button.text == tact_add and number_of_tacts < 6:
                        number_of_tacts += 1
                        temp_tact = f"{TACT_PART} {number_of_tacts}"
                        tact_buttons[temp_tact] = Button(
                            y=HEIGHT + BOX_SIZE // 2,
                            width=BOX_SIZE,
                            height=BOX_SIZE,
                            color=all_colors[temp_tact],
                            text=temp_tact,
                            label=temp_tact,
                        )
                        DRAWING_MODES[TACT] = {
                            **tact_button_options,
                            **tact_buttons,
                        }
                        DRAWING_MODES[PLAN] = {
                            **plan_buttons_options,
                            **plan_buttons,
                            **tact_buttons,
                        }
                        button_sleep()
                    elif button.text == tact_delete and number_of_tacts > 2:
                        tact_deleted(grid, number_of_tacts)
                        del tact_buttons[list(tact_buttons)[-1]]
                        DRAWING_MODES[TACT] = {
                            **tact_button_options,
                            **tact_buttons,
                        }
                        DRAWING_MODES[PLAN] = {
                            **plan_buttons_options,
                            **plan_buttons,
                            **tact_buttons,
                        }
                        number_of_tacts -= 1
                        button_sleep()
                    elif (
                        current_mode == DRAW_SCTRUCTURE
                        and button.text in draw_structure_buttons
                    ):
                        current_structure = button.text
                    elif current_mode == TACT and TACT_PART in button.text:
                        tact_id = button.text
                    elif current_mode == PLAN and button.text in plan_buttons:
                        current_status = button.text
                    elif current_mode == PLAN and button.text in NO_TACT:
                        active_tact_for_planing = None
                    elif current_mode == PLAN and button.text in tact_buttons:
                        active_tact_for_planing = button.text
