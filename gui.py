import tkinter as tk
import tkinter.font as tk_font
from tkinter import ttk
from PIL import Image, ImageTk, ImageDraw

from utils import *


class AutoScrollbar(ttk.Scrollbar):
    """A scrollbar that hides itself if it's not needed.
    Works only if you use the grid geometry manager"""

    def set(self, lo, hi):
        if float(lo) <= 0.0 and float(hi) >= 1.0:
            self.grid_remove()
        else:
            self.grid()
            ttk.Scrollbar.set(self, lo, hi)

    def pack(self, **kw):
        raise tk.TclError("Cannot use pack with this widget")

    def place(self, **kw):
        raise tk.TclError("Cannot use place with this widget")


class Zoom_Advanced(ttk.Frame):
    """Advanced zoom of the image"""

    def __init__(self, mainframe):
        """Initialize the main Frame"""
        ttk.Frame.__init__(self, master=mainframe)
        # Create canvas and put image on it
        self.tk_canvas = tk.Canvas(self.master, highlightthickness=0)
        self.tk_canvas.grid(row=0, column=1, sticky="nswe")
        self.tk_canvas.update()  # wait till canvas is created

        # define font
        button_font = tk_font.Font(size=PROJECT_INFO_TEXT_SIZE)

        # initial values
        self.drawing_mode_id = -1
        self.current_tact = None
        self.current_structure = None
        self.current_status = None
        self.current_floor_id = 0
        self.current_mode = PLAN
        self.erase_mode = False
        self.active_tact_for_planing = f"{TACT_PART} 1"
        self.all_floor_level_info = list()
        self.cursor_size = 1
        self.draw_text_on_canvas = False
        self.text_x = 0
        self.text_y = 0
        self.shift_x = None
        self.shift_y = None
        self.drawing_direction = None
        self.comments = list()

        self.current_day = pd.Timestamp(datetime.date.today())
        self.today_string = self.current_day.strftime("%A-%d-%m-%Y")
        self.today_string = translate_days_to_german(self.today_string)

        for floor_id, image_file in enumerate(full_image_path):
            new_floor_level = Floor_level_info(
                image_file, full_image_path[image_file], floor_id
            )
            image = Image.open(full_image_path[image_file])  # open image
            image_file_width, image_file_height = image.size
            try:
                pixel_history = self.load_pixel_info(new_floor_level.full_path_xlsx)
            except FileNotFoundError as e:
                pixel_history = dict()
                print(f"File {new_floor_level.full_path_xlsx} not found")
            new_floor_level.grid = self.init_grid(
                image_file_width, image_file_height, pixel_history
            )
            self.all_floor_level_info.append(new_floor_level)

        try:
            self.comments = pd.read_excel(path_to_comments).to_dict("records")
        except:
            print(f"File with comments not found")

        self.current_image = full_image_path[
            list(full_image_path)[self.current_floor_id]
        ]

        # Functions for buttons
        def change_cursor_size(cursor_size_delta):
            if cursor_size_delta > 0:
                self.cursor_size = min(55, self.cursor_size + pixel_size_increase)
            else:
                self.cursor_size = max(1, self.cursor_size - pixel_size_increase)
            self.cursor_size_text.config(text=f"{CURSOR_SIZE}: {self.cursor_size}")

        def change_tact(new_tact):
            if self.current_mode == TACT and new_tact == None:
                self.erase_mode = True
            else:
                self.current_tact = new_tact
                self.active_tact_for_planing = new_tact
                self.erase_mode = False

        def change_status(new_status):
            self.current_status = new_status
            self.erase_mode = False

        def change_draw_structure(new_structure):
            self.current_structure = new_structure
            self.erase_mode = False

        def change_day(day_delta):
            self.current_day += day_delta * german_business_day
            self.today_string = self.current_day.strftime("%A-%d-%m-%Y")
            for german_week_day in GERMAN_WEEK_DAYS:
                self.today_string = self.today_string.replace(*german_week_day)
            self.current_day_text.config(text=self.today_string)
            self.delete_all_rect()
            self.delete_all_comments()
            self.draw_grid_for_plan(
                self.all_floor_level_info[self.current_floor_id],
                self.current_day,
                self.current_mode,
            )
            self.draw_image(path_to_temp_image)
            self.draw_grid()

        def change_floor(floor_delta):
            if floor_delta > 0:
                self.current_floor_id = min(
                    floor_delta + self.current_floor_id, len(full_image_path) - 1
                )
            elif floor_delta < 0:
                self.current_floor_id = max(floor_delta + self.current_floor_id, 0)
            self.delete_all_rect()
            self.delete_all_comments()
            self.current_image = full_image_path[
                list(full_image_path)[self.current_floor_id]
            ]
            self.current_floor_text.config(
                text=self.all_floor_level_info[self.current_floor_id].floor_name
            )
            self.draw_grid_for_plan(
                self.all_floor_level_info[self.current_floor_id],
                self.current_day,
                self.current_mode,
            )
            self.draw_image(path_to_temp_image)
            self.draw_grid()
            self.erase_mode = False
            self.current_tact = None
            self.current_structure = None
            self.current_status = None

        def change_mode():
            self.drawing_mode_id = (self.drawing_mode_id + 1) % len(
                self.drawing_mode_frames
            )
            self.current_mode = list(self.drawing_mode_frames)[self.drawing_mode_id]
            for the_frame in self.drawing_mode_frames[self.current_mode]:
                the_frame.tkraise()
            self.delete_all_rect()
            self.delete_all_comments()
            self.draw_grid_for_plan(
                self.all_floor_level_info[self.current_floor_id],
                self.current_day,
                self.current_mode,
            )
            self.draw_image(path_to_temp_image)
            self.draw_grid()
            self.erase_mode = False
            self.current_tact = None
            self.current_structure = None
            self.current_status = None

        def save_floor_information():
            self.save_pixel_info(self.all_floor_level_info, make_time_plan=True)

        def print_week_planning():
            weekdays_to_print = weekdays_of_current_week(self.current_day)

            for floor in self.all_floor_level_info:
                folder_with_floor = floor.full_path_image.replace(floor.image_name, "")
                floor.folder_with_print = os.path.join(
                    folder_with_floor, "output", floor.floor_name
                )
                try:
                    os.mkdir(floor.folder_with_print)
                except OSError as e:
                    e
                for weekday in weekdays_to_print:
                    self.draw_grid_for_print(floor, weekday)
            print("all images created")

        def erase_mode_activate():
            grid = self.all_floor_level_info[self.current_floor_id].grid
            for i, row in enumerate(grid):
                for j, row_cell in enumerate(row):
                    current_pixel = grid[i][j]
                    self.tk_canvas.delete(f"{i}-{j}")
                    self.all_rects.discard(f"{i}-{j}")
                    for step in current_pixel.status:
                        current_pixel.status[step].discard(self.current_day)
                        if step == POUR_CONCRETE and (
                            current_pixel.type_structure == CONCRETE
                            or current_pixel.type_structure == PREFABRICATED_PART
                        ):
                            current_pixel.status[PART_COMPLETE].discard(
                                self.current_day + 1 * german_business_day
                            )

        def add_text():
            self.draw_text_on_canvas = True

        def delete_text():
            temp_comments = list()
            for comment in self.comments:
                if (
                    self.current_day == comment["comment_day"]
                    and self.current_floor_id == comment["comment_floor_id"]
                ):
                    self.tk_canvas.delete(comment["comment_tag"])
                else:
                    temp_comments.append(comment)
            self.comments = temp_comments[::]

        # Navigation menu on the right (tact)
        self.right_frame_tact = tk.Frame(master=self.master)

        # Buttons for the navigation menu on the right (tact)
        self.next_floor_tact = tk.Button(
            master=self.right_frame_tact,
            padx=2,
            pady=2,
            text=NEXT_FLOOR,
            command=lambda: change_floor(1),
            bg=all_colors[NEXT_FLOOR],
        )
        self.next_floor_tact["font"] = button_font
        self.next_floor_tact.grid(
            row=0, column=0, sticky="nswe", padx=3, pady=3, columnspan=3
        )

        self.previous_floor_tact = tk.Button(
            master=self.right_frame_tact,
            padx=2,
            pady=2,
            text=PREVIOUS_FLOOR,
            command=lambda: change_floor(-1),
            bg=all_colors[PREVIOUS_FLOOR],
        )
        self.previous_floor_tact["font"] = button_font
        self.previous_floor_tact.grid(
            row=1, column=0, sticky="nswe", padx=3, pady=3, columnspan=3
        )

        # Information text for the tacts
        self.tact_info_text = tk.Label(
            self.right_frame_tact,
            text=TACT_LONG,
            font=("Arial", PROJECT_INFO_TEXT_SIZE),
        )
        self.tact_info_text.grid(row=2, column=0, sticky="nswe", padx=3, columnspan=3)

        # adding the tact buttons in tact mode
        tact_buttons_for_tact_mode = [
            tk.Button(
                master=self.right_frame_tact,
                padx=1,
                pady=1,
                text=tact_.replace(TACT_PART + " ", ""),
                command=lambda tact_=tact_: change_tact(tact_),
                bg=tact_color_dict[tact_],
            )
            for i, tact_ in enumerate(tact_color_dict)
        ]

        for i, tact_button in enumerate(tact_buttons_for_tact_mode):
            tact_button["font"] = button_font
            tact_button.grid(
                row=3 + i % 10, column=i // 10, sticky="nswe", padx=2, pady=2
            )

        # Placing all the buttons on main frame (tact)
        self.right_frame_tact.grid(row=0, column=2, sticky="nswe", padx=10, pady=10)

        # Navigation menu on the right (plan)
        self.right_frame_plan = tk.Frame(master=self.master)

        # Buttons for the navigation menu on the right (plan)
        self.next_floor_plan = tk.Button(
            master=self.right_frame_plan,
            padx=2,
            pady=2,
            text=NEXT_FLOOR,
            command=lambda: change_floor(1),
            bg=WHITE,
        )
        self.next_floor_plan["font"] = button_font
        self.next_floor_plan.grid(
            row=0, column=0, sticky="nswe", padx=3, pady=3, columnspan=3
        )

        self.previous_floor_plan = tk.Button(
            master=self.right_frame_plan,
            padx=2,
            pady=2,
            text=PREVIOUS_FLOOR,
            command=lambda: change_floor(-1),
            bg=WHITE,
        )
        self.previous_floor_plan["font"] = button_font
        self.previous_floor_plan.grid(
            row=1, column=0, sticky="nswe", padx=3, pady=3, columnspan=3
        )

        # Information text for the tacts for plan mode
        self.tact_info_for_plan_text = tk.Label(
            self.right_frame_plan,
            text=TACT_LONG,
            font=("Arial", PROJECT_INFO_TEXT_SIZE),
        )
        self.tact_info_for_plan_text.grid(
            row=2, column=0, sticky="nswe", padx=3, columnspan=3
        )

        self.no_tact = tk.Button(
            master=self.right_frame_plan,
            padx=2,
            pady=2,
            text=NO_TACT,
            command=lambda: change_tact(None),
            bg=all_colors[NO_TACT],
        )
        self.no_tact["font"] = button_font
        self.no_tact.grid(row=3, column=0, sticky="nswe", padx=3, pady=3, columnspan=3)

        # adding the tact buttons in plan mode
        tact_buttons_in_plan_mode = [
            tk.Button(
                master=self.right_frame_plan,
                padx=1,
                pady=1,
                text=tact_.replace(TACT_PART + " ", ""),
                command=lambda tact_=tact_: change_tact(tact_),
                bg=WHITE,
            )
            for tact_ in tact_color_dict
        ]

        for i, tact_button in enumerate(tact_buttons_in_plan_mode):
            tact_button["font"] = button_font
            tact_button.grid(
                row=4 + i % 10, column=i // 10, sticky="nswe", padx=1, pady=1
            )

        # Placing all the buttons on main frame (plan)
        self.right_frame_plan.grid(row=0, column=2, sticky="nswe", padx=10, pady=10)

        # Navigation menu on the right (draw)
        self.right_frame_draw = tk.Frame(master=self.master)

        # Buttons for the navigation menu on the right (draw)
        self.next_floor_draw = tk.Button(
            master=self.right_frame_draw,
            padx=2,
            pady=2,
            text=NEXT_FLOOR,
            command=lambda: change_floor(1),
            bg=all_colors[NEXT_FLOOR],
        )
        self.next_floor_draw["font"] = button_font
        self.next_floor_draw.grid(row=0, column=0, sticky="nswe", padx=3, pady=3)

        self.previous_floor_draw = tk.Button(
            master=self.right_frame_draw,
            padx=2,
            pady=2,
            text=PREVIOUS_FLOOR,
            command=lambda: change_floor(-1),
            bg=all_colors[PREVIOUS_FLOOR],
        )
        self.previous_floor_draw["font"] = button_font
        self.previous_floor_draw.grid(row=1, column=0, sticky="nswe", padx=3, pady=3)

        # Placing all the buttons on main frame (draw)
        self.right_frame_draw.grid(row=0, column=2, sticky="nswe", padx=10, pady=10)

        # Navigation menu on the left
        self.left_frame = tk.Frame(master=self.master)

        # Buttons for the navigation menu on the left (tact, plan and draw)
        self.draw_mode = tk.Button(
            master=self.left_frame,
            padx=2,
            pady=2,
            text=DRAW_MODE,
            command=change_mode,
            bg=all_colors[DRAW_MODE],
        )
        self.draw_mode["font"] = button_font
        self.draw_mode.grid(row=0, column=0, sticky="nswe", padx=3, pady=3)

        self.save_button = tk.Button(
            master=self.left_frame,
            padx=2,
            pady=2,
            text=SAVE,
            command=save_floor_information,
            bg=all_colors[SAVE],
        )
        self.save_button["font"] = button_font
        self.save_button.grid(row=1, column=0, sticky="nswe", padx=3, pady=3)

        self.print_button = tk.Button(
            master=self.left_frame,
            padx=2,
            pady=2,
            text=PRINT,
            command=print_week_planning,
            bg=all_colors[PRINT],
        )
        self.print_button["font"] = button_font
        self.print_button.grid(row=2, column=0, sticky="nswe", padx=3, pady=3)

        # Information text (cursor size)
        self.cursor_size_text = tk.Label(
            self.left_frame,
            text=f"{CURSOR_SIZE}: {self.cursor_size}",
            font=("Arial", PROJECT_INFO_TEXT_SIZE),
        )
        self.cursor_size_text.grid(row=3, column=0, sticky="nswe", padx=3)

        self.cursor_bigger = tk.Button(
            master=self.left_frame,
            padx=2,
            pady=2,
            text=BIGGER,
            command=lambda: change_cursor_size(1),
            bg=all_colors[BIGGER],
        )
        self.cursor_bigger["font"] = button_font
        self.cursor_bigger.grid(row=4, column=0, sticky="nswe", padx=3, pady=3)

        self.cursor_smaller = tk.Button(
            master=self.left_frame,
            padx=2,
            pady=2,
            text=SMALLER,
            command=lambda: change_cursor_size(-1),
            bg=all_colors[SMALLER],
        )
        self.cursor_smaller["font"] = button_font
        self.cursor_smaller.grid(row=5, column=0, sticky="nswe", padx=3, pady=3)

        # Placing all the buttons on main frame (tact, plan and draw)
        self.left_frame.grid(row=0, column=0, sticky="nswe", padx=10, pady=10)

        # Information text on the bottom (current day and file name)
        self.current_day_info = tk.Frame(master=self.master)
        self.current_day_text = tk.Label(
            self.current_day_info,
            text=self.today_string,
            font=("Arial", PROJECT_INFO_TEXT_SIZE),
        )
        self.current_day_text.grid(row=0, column=0, sticky="w", padx=3)
        self.current_day_info.grid(row=1, column=0, sticky="nswe", padx=2, pady=2)

        # Information text on the bottom (floor name)
        self.current_floor_info = tk.Frame(master=self.master)
        self.current_floor_text = tk.Label(
            self.current_floor_info,
            text=self.all_floor_level_info[self.current_floor_id].floor_name,
            font=("Arial", PROJECT_INFO_TEXT_SIZE),
        )
        self.current_floor_text.grid(row=0, column=0, sticky="e", padx=3)
        self.current_floor_info.grid(row=1, column=1, sticky="nswe", padx=2, pady=2)

        # Navigation menu on the bottom (tact)
        self.bottom_frame_tact = tk.Frame(master=self.master)

        # Placing all the buttons on main frame (tact)
        self.bottom_frame_tact.grid(
            row=2, column=0, sticky="nswe", padx=10, pady=10, columnspan=3
        )

        # Navigation menu on the bottom (plan)
        self.bottom_frame_plan = tk.Frame(master=self.master)

        # Buttons for the navigation menu on the bottom (plan)
        self.last_date = tk.Button(
            master=self.bottom_frame_plan,
            padx=2,
            pady=2,
            text=LAST_DAY,
            command=lambda: change_day(-1),
            bg=all_colors[LAST_DAY],
        )
        self.last_date["font"] = button_font
        self.last_date.grid(row=0, column=0, sticky="nswe", padx=3, pady=3)

        self.next_date = tk.Button(
            master=self.bottom_frame_plan,
            padx=2,
            pady=2,
            text=NEXT_DAY,
            command=lambda: change_day(1),
            bg=all_colors[NEXT_DAY],
        )
        self.next_date["font"] = button_font
        self.next_date.grid(row=0, column=1, sticky="nswe", padx=3, pady=3)

        self.formwork = tk.Button(
            master=self.bottom_frame_plan,
            padx=2,
            pady=2,
            text=FORMWORK,
            command=lambda: change_status(FORMWORK),
            bg=all_colors[FORMWORK],
        )
        self.formwork["font"] = button_font
        self.formwork.grid(row=0, column=2, sticky="nswe", padx=3, pady=3)

        self.reinforce = tk.Button(
            master=self.bottom_frame_plan,
            padx=2,
            pady=2,
            text=REINFORCE,
            command=lambda: change_status(REINFORCE),
            bg=all_colors[REINFORCE],
        )
        self.reinforce["font"] = button_font
        self.reinforce.grid(row=0, column=3, sticky="nswe", padx=3, pady=3)

        self.pour_concrete = tk.Button(
            master=self.bottom_frame_plan,
            padx=2,
            pady=2,
            text=POUR_CONCRETE,
            command=lambda: change_status(POUR_CONCRETE),
            bg=all_colors[POUR_CONCRETE],
        )
        self.pour_concrete["font"] = button_font
        self.pour_concrete.grid(row=0, column=4, sticky="nswe", padx=3, pady=3)

        self.prefabricated_part_assembly = tk.Button(
            master=self.bottom_frame_plan,
            padx=2,
            pady=2,
            text=PREFABRICATED_PART_ASSEMBLE,
            command=lambda: change_status(PREFABRICATED_PART_ASSEMBLE),
            bg=all_colors[PREFABRICATED_PART_ASSEMBLE],
        )
        self.prefabricated_part_assembly["font"] = button_font
        self.prefabricated_part_assembly.grid(
            row=0, column=5, sticky="nswe", padx=3, pady=3
        )

        self.do_ground_job = tk.Button(
            master=self.bottom_frame_plan,
            padx=2,
            pady=2,
            text=GROUND_JOB,
            command=lambda: change_status(GROUND_JOB),
            bg=all_colors[GROUND_JOB],
        )
        self.do_ground_job["font"] = button_font
        self.do_ground_job.grid(row=0, column=6, sticky="nswe", padx=3, pady=3)

        self.do_empty_pipes = tk.Button(
            master=self.bottom_frame_plan,
            padx=2,
            pady=2,
            text=EMPTY_PIPES,
            command=lambda: change_status(EMPTY_PIPES),
            bg=all_colors[EMPTY_PIPES],
        )
        self.do_empty_pipes["font"] = button_font
        self.do_empty_pipes.grid(row=0, column=7, sticky="nswe", padx=3, pady=3)

        self.do_built_in_part = tk.Button(
            master=self.bottom_frame_plan,
            padx=2,
            pady=2,
            text=BUILT_IN_PART,
            command=lambda: change_status(BUILT_IN_PART),
            bg=all_colors[BUILT_IN_PART],
        )
        self.do_built_in_part["font"] = button_font
        self.do_built_in_part.grid(row=0, column=8, sticky="nswe", padx=3, pady=3)

        # self.do_masonry = tk.Button(
        #     master=self.bottom_frame_plan,
        #     padx=2,
        #     pady=2,
        #     text=DO_MASONRY,
        #     command=lambda: change_status(DO_MASONRY),
        #     bg=all_colors[DO_MASONRY],
        # )
        # self.do_masonry["font"] = button_font
        # self.do_masonry.grid(row=0, column=6, sticky="nswe", padx=3, pady=3)

        self.part_complete = tk.Button(
            master=self.bottom_frame_plan,
            padx=2,
            pady=2,
            text=PART_COMPLETE,
            command=lambda: change_status(PART_COMPLETE),
            bg=all_colors[PART_COMPLETE],
        )
        self.part_complete["font"] = button_font
        self.part_complete.grid(row=0, column=9, sticky="nswe", padx=3, pady=3)

        self.erase_plan = tk.Button(
            master=self.bottom_frame_plan,
            padx=2,
            pady=2,
            text=ERASE,
            command=erase_mode_activate,
            bg=all_colors[ERASE],
        )
        self.erase_plan["font"] = button_font
        self.erase_plan.grid(row=0, column=10, sticky="nswe", padx=3, pady=3)

        self.draw_text_on_canvas_button = tk.Button(
            master=self.bottom_frame_plan,
            padx=2,
            pady=2,
            text=DRAW_TEXT_ON_CANVAS,
            command=add_text,
            bg=WHITE,
        )
        self.draw_text_on_canvas_button["font"] = button_font
        self.draw_text_on_canvas_button.grid(
            row=0, column=11, sticky="nswe", padx=3, pady=3
        )

        self.delete_text_on_canvas_button = tk.Button(
            master=self.bottom_frame_plan,
            padx=2,
            pady=2,
            text=DELETE_TEXT_ON_CANVAS,
            command=delete_text,
            bg=WHITE,
        )
        self.delete_text_on_canvas_button["font"] = button_font
        self.delete_text_on_canvas_button.grid(
            row=0, column=12, sticky="nswe", padx=3, pady=3
        )

        self.new_event_button = tk.Button(
            master=self.bottom_frame_plan,
            padx=2,
            pady=2,
            text=NEW_EVENT,
            command=lambda: change_status(NEW_EVENT),
            bg=all_colors[NEW_EVENT],
        )
        self.new_event_button["font"] = button_font
        self.new_event_button.grid(row=0, column=13, sticky="nswe", padx=3, pady=3)

        # Placing all the buttons on main frame (plan)
        self.bottom_frame_plan.grid(
            row=2, column=0, sticky="nswe", padx=10, pady=10, columnspan=3
        )

        # Navigation menu on the bottom (draw)
        self.bottom_frame_draw = tk.Frame(master=self.master)

        self.concrete = tk.Button(
            master=self.bottom_frame_draw,
            padx=2,
            pady=2,
            text=CONCRETE,
            command=lambda: change_draw_structure(CONCRETE),
            bg=all_colors[CONCRETE],
            fg=WHITE,
        )
        self.concrete["font"] = button_font
        self.concrete.grid(row=0, column=0, sticky="nswe", padx=3, pady=3)

        self.prefabricated_part = tk.Button(
            master=self.bottom_frame_draw,
            padx=2,
            pady=2,
            text=PREFABRICATED_PART,
            command=lambda: change_draw_structure(PREFABRICATED_PART),
            bg=all_colors[PREFABRICATED_PART],
            fg=WHITE,
        )
        self.prefabricated_part["font"] = button_font
        self.prefabricated_part.grid(row=0, column=1, sticky="nswe", padx=3, pady=3)

        self.ground = tk.Button(
            master=self.bottom_frame_draw,
            padx=2,
            pady=2,
            text=GROUND,
            command=lambda: change_draw_structure(GROUND),
            bg=all_colors[GROUND],
            fg=WHITE,
        )
        self.ground["font"] = button_font
        self.ground.grid(row=0, column=2, sticky="nswe", padx=3, pady=3)

        # self.masonry = tk.Button(
        #     master=self.bottom_frame_draw,
        #     padx=2,
        #     pady=2,
        #     text=MASONRY,
        #     command=lambda: change_draw_structure(MASONRY),
        #     bg=all_colors[MASONRY],
        #     fg=WHITE,
        # )
        # self.masonry["font"] = button_font
        # self.masonry.grid(row=0, column=2, sticky="nswe", padx=3, pady=3)

        # Placing all the buttons on main frame (draw)
        self.bottom_frame_draw.grid(
            row=2, column=0, sticky="nswe", padx=10, pady=10, columnspan=3
        )

        self.drawing_mode_frames = {
            PLAN: [
                self.right_frame_plan,
                self.left_frame,
                self.bottom_frame_plan,
            ],
            DRAW_SCTRUCTURE: [
                self.right_frame_draw,
                self.left_frame,
                self.bottom_frame_draw,
            ],
            TACT: [
                self.right_frame_tact,
                self.left_frame,
                self.bottom_frame_tact,
            ],
        }

        # Make the canvas expandable
        self.master.rowconfigure(0, weight=1)
        self.master.columnconfigure(1, weight=1)
        # Bind events to the Canvas
        self.tk_canvas.bind("<Configure>", self.show_image)  # canvas is resized
        self.tk_canvas.bind(
            "<MouseWheel>", self.wheel
        )  # with Windows and MacOS, but not Linux
        self.tk_canvas.bind("<ButtonPress-2>", self.move_from)
        self.tk_canvas.bind("<B2-Motion>", self.move_to)
        self.tk_canvas.bind("<Button-1>", self.draw_rect)
        self.tk_canvas.bind("<B1-Motion>", self.draw_rect)
        self.tk_canvas.bind(
            "<Shift-B1-Motion>",
            lambda event: self.draw_rect(event, shift_dir=True),
        )
        self.tk_canvas.bind("<Button-3>", self.delete_rect)
        self.tk_canvas.bind("<B3-Motion>", self.delete_rect)
        #        self.tk_canvas.bind("<B3-Motion-Shift>", self.delete_rect_hor_or_vert)

        self.draw_image(self.current_image)
        self.all_rects = set()
        change_mode()
        self.current_mode = list(self.drawing_mode_frames)[self.drawing_mode_id]

    def move_from(self, event):
        """Remember previous coordinates for scrolling with the mouse"""
        self.tk_canvas.scan_mark(event.x, event.y)
        self.x_initial = event.x
        self.y_initial = event.y

    def move_to(self, event):
        """Drag (move) canvas to the new position"""
        self.tk_canvas.scan_dragto(event.x, event.y, gain=1)
        self.show_image()  # redraw the image
        self.x_correction = (event.x - self.x_initial) * self.rect_scale
        self.y_correction = (event.x - self.x_initial) * self.rect_scale

    def wheel(self, event):
        """Zoom with mouse wheel"""
        x = self.tk_canvas.canvasx(event.x)
        y = self.tk_canvas.canvasy(event.y)
        bbox = self.tk_canvas.bbox(self.container)  # get image area
        if bbox[0] < x < bbox[2] and bbox[1] < y < bbox[3]:
            pass  # Ok! Inside the image
        else:
            return  # zoom only inside image area
        scale = 1.0
        # Respond to Linux (event.num) or Windows (event.delta) wheel event
        if event.num == 5 or event.delta == -120:  # scroll down
            i = min(self.width, self.height)
            if int(i * self.imscale) < 30:
                return  # image is less than 30 pixels
            self.imscale /= self.delta
            scale /= self.delta
            self.rect_scale /= self.delta
        if event.num == 4 or event.delta == 120:  # scroll up
            i = min(self.tk_canvas.winfo_width(), self.tk_canvas.winfo_height())
            if i < self.imscale:
                return  # 1 pixel is bigger than the visible area
            self.imscale *= self.delta
            scale *= self.delta
            self.rect_scale *= self.delta
        self.tk_canvas.scale("all", x, y, scale, scale)  # rescale all canvas objects
        self.show_image()

    def show_image(self, event=None):
        """Show image on the Canvas"""
        bbox1 = self.tk_canvas.bbox(self.container)  # get image area
        # Remove 1 pixel shift at the sides of the bbox1
        bbox1 = (bbox1[0] + 1, bbox1[1] + 1, bbox1[2] - 1, bbox1[3] - 1)
        bbox2 = (
            self.tk_canvas.canvasx(0),  # get visible area of the canvas
            self.tk_canvas.canvasy(0),
            self.tk_canvas.canvasx(self.tk_canvas.winfo_width()),
            self.tk_canvas.canvasy(self.tk_canvas.winfo_height()),
        )
        bbox = [
            min(bbox1[0], bbox2[0]),
            min(bbox1[1], bbox2[1]),  # get scroll region box
            max(bbox1[2], bbox2[2]),
            max(bbox1[3], bbox2[3]),
        ]
        if (
            bbox[0] == bbox2[0] and bbox[2] == bbox2[2]
        ):  # whole image in the visible area
            bbox[0] = bbox1[0]
            bbox[2] = bbox1[2]
        if (
            bbox[1] == bbox2[1] and bbox[3] == bbox2[3]
        ):  # whole image in the visible area
            bbox[1] = bbox1[1]
            bbox[3] = bbox1[3]
        self.tk_canvas.configure(scrollregion=bbox)  # set scroll region
        x1 = max(
            bbox2[0] - bbox1[0], 0
        )  # get coordinates (x1,y1,x2,y2) of the image tile
        y1 = max(bbox2[1] - bbox1[1], 0)
        x2 = min(bbox2[2], bbox1[2]) - bbox1[0]
        y2 = min(bbox2[3], bbox1[3]) - bbox1[1]

        if (
            int(x2 - x1) > 0 and int(y2 - y1) > 0
        ):  # show image if it in the visible area
            x = min(
                int(x2 / self.imscale), self.width
            )  # sometimes it is larger on 1 pixel...
            y = min(int(y2 / self.imscale), self.height)  # ...and sometimes not
            image = self.image.crop(
                (int(x1 / self.imscale), int(y1 / self.imscale), x, y)
            )
            imagetk = ImageTk.PhotoImage(image.resize((int(x2 - x1), int(y2 - y1))))
            imageid = self.tk_canvas.create_image(
                max(bbox2[0], bbox1[0]),
                max(bbox2[1], bbox1[1]),
                anchor="nw",
                image=imagetk,
            )
            self.tk_canvas.lower(imageid)  # set image into background
            self.tk_canvas.imagetk = (
                imagetk  # keep an extra reference to prevent garbage-collection
            )

    # Drawing Image
    def draw_image(self, image_path):
        self.image = Image.open(image_path)  # open image
        self.width, self.height = self.image.size
        self.image_width_in_pixels = int(
            MAX_GRID_SIZE * self.width / (max(self.width, self.height))
        )
        self.image_height_in_pixels = int(
            MAX_GRID_SIZE * self.height / (max(self.width, self.height))
        )
        self.box_size = self.width / self.image_width_in_pixels
        self.imscale = 1.0  # scale for the canvas image
        self.delta = 1.3  # zoom magnitude
        # Put image into container rectangle and use it to set proper coordinates to the image
        self.container = self.tk_canvas.create_rectangle(
            0, 0, self.width, self.height, width=0
        )
        self.show_image()
        self.rect_scale = 1
        self.bbox = self.tk_canvas.bbox(self.container)
        self.x_initial = 0
        self.y_initial = 0
        self.x_correction = 0
        self.y_correction = 0

    # Functions for grid
    def init_grid(self, image_file_width, image_file_height, pixel_history):
        grid = list()
        for j in range(image_file_height):
            grid.append(list())
            for i in range(image_file_width):
                if f"{i}-{j}" not in pixel_history:
                    grid[j].append(Pixel(i, j))
                else:
                    type_structure = pixel_history[f"{i}-{j}"]["pixel_type_structure"]
                    status = dict()
                    if type_structure:
                        for step in working_steps[type_structure]:
                            current_step = pixel_history[f"{i}-{j}"].get(step, set())
                            status[step] = current_step
                    if (
                        NEW_EVENT in pixel_history[f"{i}-{j}"]
                        and pixel_history[f"{i}-{j}"][NEW_EVENT]
                    ):
                        status[NEW_EVENT] = pixel_history[f"{i}-{j}"][NEW_EVENT]
                    grid[j].append(
                        Pixel(
                            pixel_x=i,
                            pixel_y=j,
                            tact=pixel_history[f"{i}-{j}"]["pixel_BA"],
                            type_structure=type_structure,
                            status=status,
                        )
                    )

        return grid

    def draw_grid(self):
        bbox = self.tk_canvas.bbox(self.container)  # get image area
        print(self.current_mode)
        for grid_row in self.all_floor_level_info[self.current_floor_id].grid:
            for pixel in grid_row:
                current_fill = None
                if self.current_mode == DRAW_SCTRUCTURE and pixel.type_structure:
                    current_fill = all_colors[pixel.type_structure]
                elif self.current_mode == TACT and pixel.tact:
                    current_fill = all_colors[pixel.tact]
                elif (
                    self.current_mode == PLAN
                    and NEW_EVENT in pixel.status
                    and self.current_day in pixel.status[NEW_EVENT]
                ):
                    current_fill = all_colors[NEW_EVENT]
                elif self.current_mode == PLAN and pixel.type_structure:
                    for step in list(pixel.status)[::-1]:
                        if (
                            pixel.status[step]
                            and self.current_day in pixel.status[step]
                        ):
                            current_fill = all_colors[step]

                if current_fill:
                    self.tk_canvas.create_rectangle(
                        bbox[0]
                        + pixel.pixel_x * self.rect_scale * self.box_size
                        - self.rect_scale * self.box_size / 2,
                        bbox[1]
                        + pixel.pixel_y * self.rect_scale * self.box_size
                        - self.rect_scale * self.box_size / 2,
                        bbox[0]
                        + pixel.pixel_x * self.rect_scale * self.box_size
                        + self.rect_scale * self.box_size / 2,
                        bbox[1]
                        + pixel.pixel_y * self.rect_scale * self.box_size
                        + self.rect_scale * self.box_size / 2,
                        fill=current_fill,
                        outline="",
                        tags=f"{pixel.pixel_x}-{pixel.pixel_y}",
                    )
                    self.all_rects.add(f"{pixel.pixel_x}-{pixel.pixel_y}")
        if self.current_mode == PLAN:
            for comment in self.comments:
                if (
                    self.current_day == comment["comment_day"]
                    and self.current_floor_id == comment["comment_floor_id"]
                ):
                    self.tk_canvas.create_text(
                        bbox[0]
                        + comment["x"] * self.rect_scale * self.box_size
                        - self.rect_scale * self.box_size / 2,
                        bbox[1]
                        + comment["y"] * self.rect_scale * self.box_size
                        - self.rect_scale * self.box_size / 2,
                        text=comment["comment"],
                        tag=comment["comment_tag"],
                    )

    def draw_rect(self, event=None, shift_dir=False):
        grid = self.all_floor_level_info[self.current_floor_id].grid
        x, y = self.tk_canvas.canvasx(event.x), self.tk_canvas.canvasy(event.y)
        if shift_dir:
            if not self.shift_x and not self.shift_y:
                self.shift_x, self.shift_y = x, y
            if not self.drawing_direction:
                if self.shift_x < x or self.shift_x > x:
                    self.drawing_direction = HORIZONTAL
                elif self.shift_y < y or self.shift_y > y:
                    self.drawing_direction = VERTICAL
            if self.drawing_direction == HORIZONTAL:
                y = self.shift_y
            elif self.drawing_direction == VERTICAL:
                x = self.shift_x
        else:
            self.shift_x = None
            self.shift_y = None
            self.drawing_direction = None

        bbox = self.tk_canvas.bbox(self.container)
        if (
            bbox[0] < x - self.rect_scale * self.box_size / 2 < bbox[2]
            and bbox[1] < y - self.rect_scale * self.box_size / 2 < bbox[3]
            and bbox[0] < x + self.rect_scale * self.box_size / 2 < bbox[2]
            and bbox[1] < y + self.rect_scale * self.box_size / 2 < bbox[3]
        ):
            pass  # Ok! Inside the image
        else:
            return
        tag_x = int(self.image_width_in_pixels * (x - bbox[0]) / (bbox[2] - bbox[0]))
        tag_y = int(self.image_height_in_pixels * (y - bbox[1]) / (bbox[3] - bbox[1]))

        if self.draw_text_on_canvas:
            self.text_x = x
            self.text_y = y
            self.entry = tk.Entry(self.tk_canvas)
            self.entry.pack()
            self.entry.focus_set()
            self.entry.bind(
                "<Return>", lambda event: self.show_text(event, tag_x, tag_y)
            )
            self.tk_canvas.create_window(
                self.text_x,
                self.text_y,
                window=self.entry,
                tags="entry",
            )
            self.draw_text_on_canvas = False
            return

        for i in range(self.cursor_size):
            for j in range(self.cursor_size):
                new_x = tag_x - self.cursor_size // 2 + i
                new_y = tag_y - self.cursor_size // 2 + j
                if (
                    new_x < 0
                    or new_y < 0
                    or new_x > len(grid[0]) - 1
                    or new_y > len(grid) - 1
                ):
                    continue
                current_pixel = grid[new_y][new_x]

                # Draw structure mode
                if self.current_mode == DRAW_SCTRUCTURE:
                    if self.erase_mode == True:
                        current_pixel.type_structure = None
                        current_pixel.status = dict()
                        self.tk_canvas.delete(f"{new_x}-{new_y}")
                        self.all_rects.discard(f"{new_x}-{new_y}")
                        return

                    if (
                        current_pixel.type_structure != self.current_structure
                        and self.current_structure != None
                    ):
                        self.tk_canvas.delete(f"{new_x}-{new_y}")
                        current_pixel.type_structure = self.current_structure
                        current_pixel.status = dict()
                        for step in working_steps[self.current_structure]:
                            current_pixel.status[step] = set()

                        self.tk_canvas.create_rectangle(
                            bbox[0]
                            + new_x * self.rect_scale * self.box_size
                            - self.rect_scale * self.box_size / 2,
                            bbox[1]
                            + new_y * self.rect_scale * self.box_size
                            - self.rect_scale * self.box_size / 2,
                            bbox[0]
                            + new_x * self.rect_scale * self.box_size
                            + self.rect_scale * self.box_size / 2,
                            bbox[1]
                            + new_y * self.rect_scale * self.box_size
                            + self.rect_scale * self.box_size / 2,
                            fill=all_colors[self.current_structure],
                            outline="",
                            tags=f"{new_x}-{new_y}",
                        )
                        self.all_rects.add(f"{new_x}-{new_y}")

                # Tact mode
                elif self.current_mode == TACT:
                    if self.erase_mode == True:
                        current_pixel.tact = None
                        self.tk_canvas.delete(f"{new_x}-{new_y}")
                        self.all_rects.discard(f"{new_x}-{new_y}")
                        return

                    elif (
                        current_pixel.tact != self.current_tact
                        and self.current_tact != None
                    ):
                        self.tk_canvas.delete(f"{new_x}-{new_y}")
                        current_pixel.tact = self.current_tact
                        self.tk_canvas.create_rectangle(
                            bbox[0]
                            + new_x * self.rect_scale * self.box_size
                            - self.rect_scale * self.box_size / 2,
                            bbox[1]
                            + new_y * self.rect_scale * self.box_size
                            - self.rect_scale * self.box_size / 2,
                            bbox[0]
                            + new_x * self.rect_scale * self.box_size
                            + self.rect_scale * self.box_size / 2,
                            bbox[1]
                            + new_y * self.rect_scale * self.box_size
                            + self.rect_scale * self.box_size / 2,
                            fill=all_colors[self.current_tact],
                            outline="",
                            tags=f"{new_x}-{new_y}",
                        )
                        self.all_rects.add(f"{new_x}-{new_y}")

                # Plan mode
                elif self.current_mode == PLAN:
                    if self.erase_mode == True:
                        for step in current_pixel.status:
                            current_pixel.status[step].discard(self.current_day)
                        self.tk_canvas.delete(f"{new_x}-{new_y}")
                        self.all_rects.discard(f"{new_x}-{new_y}")
                        if self.current_status == POUR_CONCRETE and (
                            current_pixel.type_structure == CONCRETE
                            or current_pixel.type_structure == PREFABRICATED_PART
                        ):
                            current_pixel.status[PART_COMPLETE].discard(
                                self.current_day + 1 * german_business_day
                            )
                        return

                    elif (
                        self.current_status
                        in working_steps.get(current_pixel.type_structure, [])
                        and self.active_tact_for_planing == current_pixel.tact
                    ) or self.current_status == NEW_EVENT:
                        self.tk_canvas.delete(f"{new_x}-{new_y}")
                        if self.current_status not in current_pixel.status:
                            current_pixel.status[self.current_status] = set()

                        current_pixel.status[self.current_status].add(self.current_day)
                        self.tk_canvas.create_rectangle(
                            bbox[0]
                            + new_x * self.rect_scale * self.box_size
                            - self.rect_scale * self.box_size / 2,
                            bbox[1]
                            + new_y * self.rect_scale * self.box_size
                            - self.rect_scale * self.box_size / 2,
                            bbox[0]
                            + new_x * self.rect_scale * self.box_size
                            + self.rect_scale * self.box_size / 2,
                            bbox[1]
                            + new_y * self.rect_scale * self.box_size
                            + self.rect_scale * self.box_size / 2,
                            fill=all_colors[self.current_status],
                            outline="",
                            tags=f"{new_x}-{new_y}",
                        )
                        self.all_rects.add(f"{new_x}-{new_y}")
                        if self.current_status == POUR_CONCRETE and (
                            current_pixel.type_structure == CONCRETE
                            or current_pixel.type_structure == PREFABRICATED_PART
                        ):
                            current_pixel.status[PART_COMPLETE].add(
                                self.current_day + 1 * german_business_day
                            )

    def delete_rect(self, event=None):
        x, y = self.tk_canvas.canvasx(event.x), self.tk_canvas.canvasy(event.y)
        bbox = self.tk_canvas.bbox(self.container)
        tag_x = int(self.image_width_in_pixels * (x - bbox[0]) / (bbox[2] - bbox[0]))
        tag_y = int(self.image_height_in_pixels * (y - bbox[1]) / (bbox[3] - bbox[1]))
        grid = self.all_floor_level_info[self.current_floor_id].grid
        for i in range(self.cursor_size):
            for j in range(self.cursor_size):
                new_x = tag_x - self.cursor_size // 2 + i
                new_y = tag_y - self.cursor_size // 2 + j
                if (
                    new_x < 0
                    or new_y < 0
                    or new_x > len(grid[0]) - 1
                    or new_y > len(grid) - 1
                ):
                    return
                current_pixel = grid[new_y][new_x]
                self.tk_canvas.delete(f"{new_x}-{new_y}")
                self.all_rects.discard(f"{new_x}-{new_y}")
                if self.current_mode == DRAW_SCTRUCTURE:
                    current_pixel.type_structure = None
                    current_pixel.status = dict()
                elif self.current_mode == TACT:
                    current_pixel.tact = None
                elif self.current_mode == PLAN:
                    for step in current_pixel.status:
                        current_pixel.status[step].discard(self.current_day)

                    if self.current_status == POUR_CONCRETE and (
                        current_pixel.type_structure == CONCRETE
                        or current_pixel.type_structure == PREFABRICATED_PART
                    ):
                        current_pixel.status[PART_COMPLETE].discard(
                            self.current_day + 1 * german_business_day
                        )

    def delete_all_rect(self):
        for rect in self.all_rects:
            self.tk_canvas.delete(rect)

        self.all_rects = set()

    def delete_all_comments(self):
        for comment in self.comments:
            self.tk_canvas.delete(comment["comment_tag"])

    def draw_grid_for_plan(self, floor, current_day, current_mode):
        img = Image.open(floor.full_path_image)
        draw = ImageDraw.Draw(img, "RGBA")

        for i, row in enumerate(floor.grid):
            for j, pixel in enumerate(row):
                current_color_key, current_transparency = pixel.get_color_key_for_plan(
                    current_mode, current_day
                )
                if current_color_key:
                    current_r, current_g, current_b = hex_colour_to_rgb(
                        all_colors[current_color_key]
                    )
                    draw.rectangle(
                        xy=(
                            self.box_size * (pixel.pixel_x - 1),
                            self.box_size * (pixel.pixel_y - 1),
                            self.box_size * (pixel.pixel_x - 1) + self.box_size,
                            self.box_size * (pixel.pixel_y - 1) + self.box_size,
                        ),
                        outline=None,
                        width=0,
                        fill=(
                            current_r,
                            current_g,
                            current_b,
                            int(255 * current_transparency),
                        ),
                    )
        img.save(os.path.join(path_to_temp_image))

    def draw_grid_for_print(self, floor, current_day):
        img = Image.open(floor.full_path_image)
        WIDTH, HEIGHT = img.size
        TOOLBAR_HEIGHT = 100
        BOX_SIZE = 50
        blank_image = Image.new(
            mode="RGB", size=(WIDTH, HEIGHT + TOOLBAR_HEIGHT), color=WHITE
        )

        blank_image.paste(img)
        img = blank_image
        active_works_on_floor = False
        draw = ImageDraw.Draw(img, "RGBA")
        legend = set()
        for i, row in enumerate(floor.grid):
            for j, pixel in enumerate(row):
                current_color_key, current_transparency = pixel.get_color_key_for_print(
                    current_day
                )
                if current_color_key:
                    current_r, current_g, current_b = hex_colour_to_rgb(
                        all_colors[current_color_key]
                    )
                    active_works_on_floor = True
                    legend.add(current_color_key)
                    draw.rectangle(
                        xy=(
                            self.box_size * (pixel.pixel_x - 1.5),
                            self.box_size * (pixel.pixel_y - 1.5),
                            self.box_size * (pixel.pixel_x - 1.5) + self.box_size,
                            self.box_size * (pixel.pixel_y - 1.5) + self.box_size,
                        ),
                        outline=all_colors[current_color_key],
                        fill=(
                            current_r,
                            current_g,
                            current_b,
                            int(255 * current_transparency),
                        ),
                    )

        for comment in self.comments:
            if (
                # Comparison of Timestamp with datetime.date is deprecated in order to match the standard library behavior. In a future version these will be considered non-comparable. Use 'ts == pd.Timestamp(date)' or 'ts.date() == date' instead.
                pd.Timestamp(current_day) == comment["comment_day"]
                and floor.floor_id == comment["comment_floor_id"]
            ):
                try:
                    draw.text(
                        (self.box_size * comment["x"], self.box_size * comment["y"]),
                        str(comment["comment"]),
                        font=project_font_path,
                        fill=BLACK,
                    )
                except Exception as e:
                    print(f"Problem with {comment}")
                    print(e)
        if active_works_on_floor:
            today_string = current_day.strftime("%A-%d-%m-%Y")
            for german_week_day in GERMAN_WEEK_DAYS:
                today_string = today_string.replace(*german_week_day)
            draw.text(
                (10, 10),
                today_string,
                font=project_font_path,
                fill=BLACK,
            )
            draw.text((600, 10), floor.floor_name, font=project_font_path, fill=BLACK)
            for i, work_step in enumerate(legend):
                box_x = 10 * (1 + i) + i * BOX_SIZE
                box_y = HEIGHT + BOX_SIZE // 2
                draw.rectangle(
                    xy=(
                        box_x,
                        box_y,
                        box_x + BOX_SIZE,
                        box_y + BOX_SIZE,
                    ),
                    outline=BLACK,
                    fill=all_colors[work_step],
                )
                draw.text(
                    (box_x, box_y + int(BOX_SIZE // 2.5)),
                    long_names_for_legend.get(work_step, work_step),
                    font=project_font_path_small,
                    fill=BLACK,
                )
            img.save(
                os.path.join(
                    floor.folder_with_print,
                    floor.floor_name + "_" + str(current_day) + ".jpg",
                )
            )

    def save_pixel_info(self, all_floor_level_info, make_time_plan=True):
        all_floor_levels = list()
        for temp_floor in all_floor_level_info:
            grid = temp_floor.grid
            pixel_info = list()
            for i, row in enumerate(grid):
                for j, pixel in enumerate(row):
                    if pixel.tact or pixel.type_structure or pixel.status:
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
                            self.return_only_from_set, function_for_set=min
                        )
                        df[f"{df_column}_letzter_Tag"] = df[df_column].apply(
                            self.return_only_from_set, function_for_set=max
                        )
                all_floor_levels.append(df)
        print("Files saved successfully")

        df_comments = pd.DataFrame(self.comments)
        df_comments.to_excel(path_to_comments, index=False)
        print("Comments saved successfully")

        if make_time_plan:
            all_floor_levels_df = pd.concat(all_floor_levels)
            all_floor_levels_df["pixel_BA"] = all_floor_levels_df["pixel_BA"].replace(
                {None: "Kein BA"}
            )
            floor_levels_df_grouped = (
                all_floor_levels_df.groupby(
                    ["geschoss", "pixel_BA", "pixel_type_structure"]
                )
                .agg([min, max])
                .reset_index()
            )
            floor_levels_df_grouped.columns = [
                "_".join(column) for column in floor_levels_df_grouped.columns
            ]
            floor_levels_df_grouped = floor_levels_df_grouped[
                [
                    column
                    for column in floor_levels_df_grouped.columns
                    if column in ["geschoss_", "pixel_BA_", "pixel_type_structure_"]
                    or "erster_Tag_min" in column
                    or "letzter_Tag_max" in column
                ]
            ]
            floor_levels_melted = floor_levels_df_grouped.melt(
                id_vars=["geschoss_", "pixel_BA_", "pixel_type_structure_"],
                var_name="Vorgang",
                value_name="Datum",
            ).dropna()
            floor_levels_melted["Zeilenbezeichnung"] = (
                floor_levels_melted["geschoss_"]
                + "_"
                + +floor_levels_melted["pixel_BA_"]
                + "_"
                + +floor_levels_melted["pixel_type_structure_"]
                + "_"
                + +floor_levels_melted["Vorgang"].apply(lambda x: x.split("_")[0])
            )
            floor_levels_melted = floor_levels_melted[["Zeilenbezeichnung", "Datum"]]
            floor_levels_cleaned = (
                floor_levels_melted.groupby("Zeilenbezeichnung")
                .agg([min, max])
                .reset_index()
            )
            floor_levels_cleaned.columns = ["Zeilenbezeichnung", "Start", "Ende"]
            floor_levels_cleaned["Vorgang"] = floor_levels_cleaned[
                "Zeilenbezeichnung"
            ].apply(lambda x: x.split("_")[-1])
            floor_levels_cleaned = floor_levels_cleaned[
                ["Zeilenbezeichnung", "Vorgang", "Start", "Ende"]
            ]
            floor_levels_cleaned["Ende"] = floor_levels_cleaned[
                "Ende"
            ] + datetime.timedelta(days=1)

            # drawing Gantt Chart
            fig = px.timeline(
                floor_levels_cleaned,
                x_start="Start",
                x_end="Ende",
                y="Zeilenbezeichnung",
                color="Vorgang",
                color_discrete_map=color_map_for_plotly,
                title="Terminplan",
            )
            fig.update_yaxes(autorange="reversed")
            # Set the x-axis format to show the weekday in the date
            fig.update_xaxes(
                tickformat="%A %d-%m",
                # ticktext=translate_days_to_german("%A %d-%m"),
                #     tickvals=pd.date_range(start=df['Start'].min(), end=df['Finish'].max(), freq='D'),
                #     ticktext=pd.date_range(start=df['Start'].min(), end=df['Finish'].max(), freq='D').strftime('%m-%d (%A)'),
            )
            fig.write_html(os.path.join(path_to_image_folder, "zeitplan.html"))

            # writng xlsx file
            floor_levels_cleaned.to_excel(
                os.path.join(path_to_image_folder, "zeitplan.xlsx"), index=False
            )
            print("Gantt chart created successfully")

    def load_pixel_info(self, pixel_info_file):
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

    def return_only_from_set(self, value, function_for_set):
        # returns max or min from given set
        if type(value) == set and value:
            return function_for_set(value)
        else:
            return None

    def show_text(self, event, tag_x=0, tag_y=0):
        text = self.entry.get()
        self.tk_canvas.delete("entry")
        self.entry = None
        temp_tag = f"{tag_x}-{tag_y}-text"
        self.tk_canvas.create_text(self.text_x, self.text_y, text=text, tag=temp_tag)
        self.comments.append(
            {
                "x": tag_x,
                "y": tag_y,
                "comment": text,
                "comment_day": self.current_day,
                "comment_floor_id": self.current_floor_id,
                "comment_tag": temp_tag,
            }
        )


root = tk.Tk()

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight() - 100
root.geometry(f"{screen_width}x{screen_height}-1+1")

app = Zoom_Advanced(root)

root.mainloop()
