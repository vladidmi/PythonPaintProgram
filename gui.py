import tkinter as tk
import tkinter.font as tk_font
from tkinter import ttk
from PIL import Image, ImageTk

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
        self.canvas = tk.Canvas(self.master, highlightthickness=0)
        self.canvas.grid(row=0, column=1, sticky="nswe")
        self.canvas.update()  # wait till canvas is created

        # define font
        button_font = tk_font.Font(size=PROJECT_INFO_TEXT_SIZE)

        # initial values
        self.drawing_mode_id = -1
        self.current_tact = None
        self.current_structure = None
        self.current_status = None
        self.current_floor_id = 0
        self.erase_mode = False
        self.active_tact_for_planing = f"{TACT_PART} 1"
        self.all_floor_level_info = list()
        self.cursor_size = 1

        self.current_day = pd.Timestamp(datetime.date.today())
        self.today_string = self.current_day.strftime("%A-%d-%m-%Y")
        for german_week_day in GERMAN_WEEK_DAYS:
            self.today_string = self.today_string.replace(*german_week_day)

        for image_file in full_image_path:
            new_floor_level = Floor_level_info(image_file, full_image_path[image_file])
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

        # Functions for buttons
        def blank_function():
            pass
        
        def change_cursor_size(cursor_size_delta):
            if cursor_size_delta>0:
                self.cursor_size = min(15,self.cursor_size+2)
            else:
                self.cursor_size = max(1,self.cursor_size-2)
            self.cursor_size_text.config(text = f"Zeigergröße: {self.cursor_size}")

        def change_tact(new_tact):
            self.current_tact = new_tact
            self.active_tact_for_planing = new_tact
            

        def change_draw_structure(new_structure):
            self.current_structure = new_structure

        def change_day(day_delta):
            self.current_day += day_delta * german_business_day
            self.today_string = self.current_day.strftime("%A-%d-%m-%Y")
            for german_week_day in GERMAN_WEEK_DAYS:
                self.today_string = self.today_string.replace(*german_week_day)
            self.current_day_text.config(text=self.today_string)

        def change_floor(floor_delta):
            if floor_delta > 0:
                self.current_floor_id = min(
                    floor_delta + self.current_floor_id, len(full_image_path) - 1
                )
            elif floor_delta < 0:
                self.current_floor_id = max(floor_delta + self.current_floor_id, 0)
            self.delete_all_rect()
            current_image = full_image_path[
                list(full_image_path)[self.current_floor_id]
            ]
            self.draw_image(current_image)
            self.current_floor_text.config(
                text=self.all_floor_level_info[self.current_floor_id].floor_name
            )

        def change_mode():
            self.drawing_mode_id = (self.drawing_mode_id + 1) % len(
                self.drawing_mode_frames
            )
            self.current_mode = list(self.drawing_mode_frames)[self.drawing_mode_id]
            for the_frame in self.drawing_mode_frames[self.current_mode]:
                the_frame.tkraise()
            self.delete_all_rect()
            if self.current_mode == DRAW_SCTRUCTURE:
                bbox = self.canvas.bbox(self.container)  # get image area
                for grid_row in self.all_floor_level_info[self.current_floor_id].grid:
                    for pixel in grid_row:
                        if pixel.type_structure:
                            self.canvas.create_rectangle(
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
                                fill=all_colors[pixel.type_structure],
                                tags=f"{pixel.pixel_x}-{pixel.pixel_y}",
                            )
                            self.all_rects.add(f"{pixel.pixel_x}-{pixel.pixel_y}")

        def save_floor_information():
            self.save_pixel_info(self.all_floor_level_info, make_time_plan=False)

        # Navigation menu on the right (tact and plan)
        self.right_frame_tact_and_plan = tk.Frame(master=self.master)

        # Buttons for the navigation menu on the right (tact and plan)
        self.next_floor_tact_and_plan = tk.Button(
            master=self.right_frame_tact_and_plan,
            padx=3,
            pady=3,
            text=NEXT_FLOOR,
            command=lambda: change_floor(1),
            bg=all_colors[NEXT_FLOOR],
        )
        self.next_floor_tact_and_plan["font"] = button_font
        self.next_floor_tact_and_plan.grid(
            row=0, column=0, sticky="nswe", padx=5, pady=5
        )

        self.previous_floor_tact_and_plan = tk.Button(
            master=self.right_frame_tact_and_plan,
            padx=3,
            pady=3,
            text=PREVIOUS_FLOOR,
            command=lambda: change_floor(-1),
            bg=all_colors[PREVIOUS_FLOOR],
        )
        self.previous_floor_tact_and_plan["font"] = button_font
        self.previous_floor_tact_and_plan.grid(
            row=1, column=0, sticky="nswe", padx=5, pady=5
        )

        self.tact_1_tact_and_plan = tk.Button(
            master=self.right_frame_tact_and_plan,
            padx=3,
            pady=3,
            text=f"{TACT_PART} 1",
            command=lambda : change_tact(f"{TACT_PART} 1"),
            bg=all_colors[f"{TACT_PART} 1"],
        )
        self.tact_1_tact_and_plan["font"] = button_font
        self.tact_1_tact_and_plan.grid(row=2, column=0, sticky="nswe", padx=5, pady=5)

        self.tact_2_tact_and_plan = tk.Button(
            master=self.right_frame_tact_and_plan,
            padx=3,
            pady=3,
            text=f"{TACT_PART} 2",
            command=lambda : change_tact(f"{TACT_PART} 2"),
            bg=all_colors[f"{TACT_PART} 2"],
        )
        self.tact_2_tact_and_plan["font"] = button_font
        self.tact_2_tact_and_plan.grid(row=3, column=0, sticky="nswe", padx=5, pady=5)

        self.tact_3_tact_and_plan = tk.Button(
            master=self.right_frame_tact_and_plan,
            padx=3,
            pady=3,
            text=f"{TACT_PART} 3",
            command=lambda : change_tact(f"{TACT_PART} 3"),
            bg=all_colors[f"{TACT_PART} 3"],
        )
        self.tact_3_tact_and_plan["font"] = button_font
        self.tact_3_tact_and_plan.grid(row=4, column=0, sticky="nswe", padx=5, pady=5)

        self.tact_4_tact_and_plan = tk.Button(
            master=self.right_frame_tact_and_plan,
            padx=3,
            pady=3,
            text=f"{TACT_PART} 4",
            command=lambda : change_tact(f"{TACT_PART} 4"),
            bg=all_colors[f"{TACT_PART} 4"],
        )
        self.tact_4_tact_and_plan["font"] = button_font
        self.tact_4_tact_and_plan.grid(row=5, column=0, sticky="nswe", padx=5, pady=5)

        self.tact_5_tact_and_plan = tk.Button(
            master=self.right_frame_tact_and_plan,
            padx=3,
            pady=3,
            text=f"{TACT_PART} 5",
            command=lambda : change_tact(f"{TACT_PART} 5"),
            bg=all_colors[f"{TACT_PART} 5"],
        )
        self.tact_5_tact_and_plan["font"] = button_font
        self.tact_5_tact_and_plan.grid(row=6, column=0, sticky="nswe", padx=5, pady=5)

        self.tact_6_tact_and_plan = tk.Button(
            master=self.right_frame_tact_and_plan,
            padx=3,
            pady=3,
            text=f"{TACT_PART} 6",
            command=lambda : change_tact(f"{TACT_PART} 6"),
            bg=all_colors[f"{TACT_PART} 6"],
        )
        self.tact_6_tact_and_plan["font"] = button_font
        self.tact_6_tact_and_plan.grid(row=7, column=0, sticky="nswe", padx=5, pady=5)

        self.no_tact_tact_and_plan = tk.Button(
            master=self.right_frame_tact_and_plan,
            padx=3,
            pady=3,
            text=NO_TACT,
            command=lambda : change_tact(None),
            bg=all_colors[NO_TACT],
        )
        self.no_tact_tact_and_plan["font"] = button_font
        self.no_tact_tact_and_plan.grid(row=8, column=0, sticky="nswe", padx=5, pady=5)

        # Placing all the buttons on main frame (tact and plan)
        self.right_frame_tact_and_plan.grid(
            row=0, column=2, sticky="nswe", padx=10, pady=10
        )

        # Navigation menu on the right (draw)
        self.right_frame_draw = tk.Frame(master=self.master)

        # Buttons for the navigation menu on the right (draw)
        self.next_floor_draw = tk.Button(
            master=self.right_frame_draw,
            padx=3,
            pady=3,
            text=NEXT_FLOOR,
            command=lambda: change_floor(1),
            bg=all_colors[NEXT_FLOOR],
        )
        self.next_floor_draw["font"] = button_font
        self.next_floor_draw.grid(row=0, column=0, sticky="nswe", padx=5, pady=5)

        self.previous_floor_draw = tk.Button(
            master=self.right_frame_draw,
            padx=3,
            pady=3,
            text=PREVIOUS_FLOOR,
            command=lambda: change_floor(-1),
            bg=all_colors[PREVIOUS_FLOOR],
        )
        self.previous_floor_draw["font"] = button_font
        self.previous_floor_draw.grid(row=1, column=0, sticky="nswe", padx=5, pady=5)

        # Placing all the buttons on main frame (tact and plan)
        self.right_frame_draw.grid(row=0, column=2, sticky="nswe", padx=10, pady=10)

        # Navigation menu on the left
        self.left_frame = tk.Frame(master=self.master)

        # Buttons for the navigation menu on the left (tact, plan and draw)
        self.draw_mode = tk.Button(
            master=self.left_frame,
            padx=3,
            pady=3,
            text=DRAW_MODE,
            command=change_mode,
            bg=all_colors[DRAW_MODE],
        )
        self.draw_mode["font"] = button_font
        self.draw_mode.grid(row=0, column=0, sticky="nswe", padx=5, pady=5)

        # Information text on the bottom (cursor size)
        self.cursor_size_text = tk.Label(
            self.left_frame,
            text=f'Zeigergröße: {self.cursor_size}',
            font=("Arial", BUTTON_TEXT_SIZE),
        )
        self.cursor_size_text.grid(row=1, column=0, sticky="nswe", padx=5)

        self.cursor_bigger = tk.Button(
            master=self.left_frame,
            padx=3,
            pady=3,
            text=BIGGER,
            command=lambda : change_cursor_size(1),
            bg=all_colors[BIGGER],
        )
        self.cursor_bigger["font"] = button_font
        self.cursor_bigger.grid(row=2, column=0, sticky="nswe", padx=5, pady=5)

        self.cursor_smaller = tk.Button(
            master=self.left_frame,
            padx=3,
            pady=3,
            text=SMALLER,
            command=lambda : change_cursor_size(-1),
            bg=all_colors[SMALLER],
        )
        self.cursor_smaller["font"] = button_font
        self.cursor_smaller.grid(row=3, column=0, sticky="nswe", padx=5, pady=5)

        self.save_button = tk.Button(
            master=self.left_frame,
            padx=3,
            pady=3,
            text=SAVE,
            command=save_floor_information,
            bg=all_colors[SAVE],
        )
        self.save_button["font"] = button_font
        self.save_button.grid(row=4, column=0, sticky="nswe", padx=5, pady=5)

        self.print_button = tk.Button(
            master=self.left_frame,
            padx=3,
            pady=3,
            text=PRINT,
            command=blank_function,
            bg=all_colors[PRINT],
        )
        self.print_button["font"] = button_font
        self.print_button.grid(row=5, column=0, sticky="nswe", padx=5, pady=5)

        # Placing all the buttons on main frame (tact, plan and draw)
        self.left_frame.grid(row=0, column=0, sticky="nswe", padx=10, pady=10)

        # Information text on the bottom (current day and file name)
        self.current_day_info = tk.Frame(master=self.master)
        self.current_day_text = tk.Label(
            self.current_day_info,
            text=self.today_string,
            font=("Arial", BUTTON_TEXT_SIZE),
        )
        self.current_day_text.grid(row=0, column=0, sticky="w", padx=5)
        self.current_day_info.grid(row=1, column=0, sticky="nswe", padx=2, pady=2)

        # Information text on the bottom (floor name)
        self.current_floor_info = tk.Frame(master=self.master)
        self.current_floor_text = tk.Label(
            self.current_floor_info,
            text=self.all_floor_level_info[self.current_floor_id].floor_name,
            font=("Arial", BUTTON_TEXT_SIZE),
        )
        self.current_floor_text.grid(row=0, column=0, sticky="e", padx=5)
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
            padx=3,
            pady=3,
            text=LAST_DAY,
            command=lambda: change_day(-1),
            bg=all_colors[LAST_DAY],
        )
        self.last_date["font"] = button_font
        self.last_date.grid(row=0, column=0, sticky="nswe", padx=5, pady=5)

        self.next_date = tk.Button(
            master=self.bottom_frame_plan,
            padx=3,
            pady=3,
            text=NEXT_DAY,
            command=lambda: change_day(1),
            bg=all_colors[NEXT_DAY],
        )
        self.next_date["font"] = button_font
        self.next_date.grid(row=0, column=1, sticky="nswe", padx=5, pady=5)

        self.formwork = tk.Button(
            master=self.bottom_frame_plan,
            padx=3,
            pady=3,
            text=FORMWORK,
            command=blank_function,
            bg=all_colors[FORMWORK],
        )
        self.formwork["font"] = button_font
        self.formwork.grid(row=0, column=2, sticky="nswe", padx=5, pady=5)

        self.reinforce = tk.Button(
            master=self.bottom_frame_plan,
            padx=3,
            pady=3,
            text=REINFORCE,
            command=blank_function,
            bg=all_colors[REINFORCE],
        )
        self.reinforce["font"] = button_font
        self.reinforce.grid(row=0, column=3, sticky="nswe", padx=5, pady=5)

        self.pour_concrete = tk.Button(
            master=self.bottom_frame_plan,
            padx=3,
            pady=3,
            text=POUR_CONCRETE,
            command=blank_function,
            bg=all_colors[POUR_CONCRETE],
        )
        self.pour_concrete["font"] = button_font
        self.pour_concrete.grid(row=0, column=4, sticky="nswe", padx=5, pady=5)

        self.prefabricated_part_assembly = tk.Button(
            master=self.bottom_frame_plan,
            padx=3,
            pady=3,
            text=PREFABRICATED_PART_ASSEMBLE,
            command=blank_function,
            bg=all_colors[PREFABRICATED_PART_ASSEMBLE],
        )
        self.prefabricated_part_assembly["font"] = button_font
        self.prefabricated_part_assembly.grid(
            row=0, column=5, sticky="nswe", padx=5, pady=5
        )

        self.do_masonry = tk.Button(
            master=self.bottom_frame_plan,
            padx=3,
            pady=3,
            text=DO_MASONRY,
            command=blank_function,
            bg=all_colors[DO_MASONRY],
        )
        self.do_masonry["font"] = button_font
        self.do_masonry.grid(row=0, column=6, sticky="nswe", padx=5, pady=5)

        self.part_complete = tk.Button(
            master=self.bottom_frame_plan,
            padx=3,
            pady=3,
            text=PART_COMPLETE,
            command=blank_function,
            bg=all_colors[PART_COMPLETE],
        )
        self.part_complete["font"] = button_font
        self.part_complete.grid(row=0, column=7, sticky="nswe", padx=5, pady=5)

        self.erase_plan = tk.Button(
            master=self.bottom_frame_plan,
            padx=3,
            pady=3,
            text=ERASE,
            command=blank_function,
            bg=all_colors[ERASE],
        )
        self.erase_plan["font"] = button_font
        self.erase_plan.grid(row=0, column=8, sticky="nswe", padx=5, pady=5)

        # Placing all the buttons on main frame (plan)
        self.bottom_frame_plan.grid(
            row=2, column=0, sticky="nswe", padx=10, pady=10, columnspan=3
        )

        # Navigation menu on the bottom (draw)
        self.bottom_frame_draw = tk.Frame(master=self.master)

        self.concrete = tk.Button(
            master=self.bottom_frame_draw,
            padx=3,
            pady=3,
            text=CONCRETE,
            command=lambda : change_draw_structure(CONCRETE),
            bg=all_colors[CONCRETE],
            fg=WHITE,
        )
        self.concrete["font"] = button_font
        self.concrete.grid(row=0, column=0, sticky="nswe", padx=5, pady=5)

        self.prefabricated_part = tk.Button(
            master=self.bottom_frame_draw,
            padx=3,
            pady=3,
            text=PREFABRICATED_PART,
            command=lambda : change_draw_structure(PREFABRICATED_PART),
            bg=all_colors[PREFABRICATED_PART],
            fg=WHITE,
        )
        self.prefabricated_part["font"] = button_font
        self.prefabricated_part.grid(row=0, column=1, sticky="nswe", padx=5, pady=5)

        self.masonry = tk.Button(
            master=self.bottom_frame_draw,
            padx=3,
            pady=3,
            text=MASONRY,
            command=lambda : change_draw_structure(MASONRY),
            bg=all_colors[MASONRY],
            fg=WHITE,
        )
        self.masonry["font"] = button_font
        self.masonry.grid(row=0, column=2, sticky="nswe", padx=5, pady=5)

        self.erase_draw = tk.Button(
            master=self.bottom_frame_draw,
            padx=3,
            pady=3,
            text=ERASE,
            command=blank_function,
            bg=all_colors[ERASE],
        )
        self.erase_draw["font"] = button_font
        self.erase_draw.grid(row=0, column=3, sticky="nswe", padx=5, pady=5)

        # Placing all the buttons on main frame (draw)
        self.bottom_frame_draw.grid(
            row=2, column=0, sticky="nswe", padx=10, pady=10, columnspan=3
        )

        self.drawing_mode_frames = {
            PLAN: [
                self.right_frame_tact_and_plan,
                self.left_frame,
                self.bottom_frame_plan,
            ],
            DRAW_SCTRUCTURE: [
                self.right_frame_draw,
                self.left_frame,
                self.bottom_frame_draw,
            ],
            TACT: [
                self.right_frame_tact_and_plan,
                self.left_frame,
                self.bottom_frame_tact,
            ],
        }

        # Make the canvas expandable
        self.master.rowconfigure(0, weight=1)
        self.master.columnconfigure(1, weight=1)
        # Bind events to the Canvas
        self.canvas.bind("<Configure>", self.show_image)  # canvas is resized
        self.canvas.bind(
            "<MouseWheel>", self.wheel
        )  # with Windows and MacOS, but not Linux
        self.canvas.bind("<ButtonPress-2>", self.move_from)
        self.canvas.bind("<B2-Motion>", self.move_to)
        self.canvas.bind("<Button-1>", self.draw_rect)
        self.canvas.bind("<B1-Motion>", self.draw_rect)
        #        self.master.bind('<Key>', self.delete_rect)
        self.canvas.bind("<Button-3>", self.delete_rect)
        self.canvas.bind("<B3-Motion>", self.delete_rect)

        current_image = full_image_path[list(full_image_path)[self.current_floor_id]]
        self.draw_image(current_image)
        self.all_rects = set()
        change_mode()
        self.current_mode = list(self.drawing_mode_frames)[self.drawing_mode_id]

    def move_from(self, event):
        """Remember previous coordinates for scrolling with the mouse"""
        self.canvas.scan_mark(event.x, event.y)
        self.x_initial = event.x
        self.y_initial = event.y

    def move_to(self, event):
        """Drag (move) canvas to the new position"""
        self.canvas.scan_dragto(event.x, event.y, gain=1)
        self.show_image()  # redraw the image
        self.x_correction = (event.x - self.x_initial) * self.rect_scale
        self.y_correction = (event.x - self.x_initial) * self.rect_scale

    def wheel(self, event):
        """Zoom with mouse wheel"""
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        bbox = self.canvas.bbox(self.container)  # get image area
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
            i = min(self.canvas.winfo_width(), self.canvas.winfo_height())
            if i < self.imscale:
                return  # 1 pixel is bigger than the visible area
            self.imscale *= self.delta
            scale *= self.delta
            self.rect_scale *= self.delta
        self.canvas.scale("all", x, y, scale, scale)  # rescale all canvas objects
        self.show_image()

    def show_image(self, event=None):
        """Show image on the Canvas"""
        bbox1 = self.canvas.bbox(self.container)  # get image area
        # Remove 1 pixel shift at the sides of the bbox1
        bbox1 = (bbox1[0] + 1, bbox1[1] + 1, bbox1[2] - 1, bbox1[3] - 1)
        bbox2 = (
            self.canvas.canvasx(0),  # get visible area of the canvas
            self.canvas.canvasy(0),
            self.canvas.canvasx(self.canvas.winfo_width()),
            self.canvas.canvasy(self.canvas.winfo_height()),
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
        self.canvas.configure(scrollregion=bbox)  # set scroll region
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
            imageid = self.canvas.create_image(
                max(bbox2[0], bbox1[0]),
                max(bbox2[1], bbox1[1]),
                anchor="nw",
                image=imagetk,
            )
            self.canvas.lower(imageid)  # set image into background
            self.canvas.imagetk = (
                imagetk  # keep an extra reference to prevent garbage-collection
            )

    # Drawing Image
    def draw_image(self, image_path):
        self.image = Image.open(image_path)  # open image
        self.width, self.height = self.image.size
        self.imscale = 1.0  # scale for the canvas image
        self.delta = 1.3  # zoom magnitude
        # Put image into container rectangle and use it to set proper coordinates to the image
        self.container = self.canvas.create_rectangle(
            0, 0, self.width, self.height, width=0
        )
        self.show_image()
        self.rect_scale = 1
        self.bbox = self.canvas.bbox(self.container)
        self.image_width_in_pixels = int(
            1000
            * (self.bbox[2] - self.bbox[0])
            / (max((self.bbox[2] - self.bbox[0]), (self.bbox[3] - self.bbox[1])))
        )
        self.image_height_in_pixels = int(
            1000
            * (self.bbox[3] - self.bbox[1])
            / (max((self.bbox[2] - self.bbox[0]), (self.bbox[3] - self.bbox[1])))
        )
        self.box_size = (self.bbox[2] - self.bbox[0]) / self.image_width_in_pixels
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
        for i, row in enumerate(self.grid):
            for j, pixel in enumerate(row):
                current_color_key, current_transparency = pixel.get_color_key(
                    self.current_mode, self.current_day
                )
                if current_color_key:
                    pixel.draw_color(current_color_key, current_transparency, i, j)

    def draw_rect(self, event=None):
        grid = self.all_floor_level_info[self.current_floor_id].grid
        x, y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
        bbox = self.canvas.bbox(self.container)
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
        if f"{tag_x}-{tag_y}" not in self.all_rects:
            self.canvas.create_rectangle(
                bbox[0]
                + tag_x * self.rect_scale * self.box_size
                - self.rect_scale * self.box_size / 2,
                bbox[1]
                + tag_y * self.rect_scale * self.box_size
                - self.rect_scale * self.box_size / 2,
                bbox[0]
                + tag_x * self.rect_scale * self.box_size
                + self.rect_scale * self.box_size / 2,
                bbox[1]
                + tag_y * self.rect_scale * self.box_size
                + self.rect_scale * self.box_size / 2,
                fill="black",
                tags=f"{tag_x}-{tag_y}",
            )
            self.all_rects.add(f"{tag_x}-{tag_y}")
        current_pixel = grid[tag_y][tag_x]
        current_pixel.type_structure = self.current_structure
        current_pixel.status = dict()
        for step in working_steps[self.current_structure]:
            current_pixel.status[step] = set()

    def delete_rect(self, event=None):
        x, y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
        bbox = self.canvas.bbox(self.container)
        tag_x = int(self.image_width_in_pixels * (x - bbox[0]) / (bbox[2] - bbox[0]))
        tag_y = int(self.image_height_in_pixels * (y - bbox[1]) / (bbox[3] - bbox[1]))
        for i in range(5):
            for j in range(5):
                self.canvas.delete(f"{tag_x+i}-{tag_y+j}")
                self.all_rects.discard(f"{tag_x+i}-{tag_y+j}")

        if event.char == "d":
            self.canvas.delete("square")

    def delete_all_rect(self):
        for rect in self.all_rects:
            self.canvas.delete(rect)

        self.all_rects = set()

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
                    active_works_on_floor = True
                    legend.add(current_color_key)
                    draw.rectangle(
                        xy=(
                            self.box_size * pixel.pixel_x,
                            self.box_size * pixel.pixel_y,
                            self.box_size * pixel.pixel_x + self.box_size,
                            self.box_size * pixel.pixel_y + self.box_size,
                        ),
                        outline=all_colors[current_color_key],
                        fill=(
                            *all_colors[current_color_key],
                            255 * current_transparency,
                        ),
                    )
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
                    fill=all_colors[legend],
                )
                draw.text(
                    (box_x + BOX_SIZE // 5, box_y + BOX_SIZE // 2),
                    legend,
                    font=project_font_path_small,
                    fill=BLACK,
                )
            img.save(
                os.path.join(
                    floor.folder_with_print,
                    floor.floor_name + "_" + str(current_day) + ".jpg",
                )
            )

    def save_pixel_info(self, all_floor_level_info, make_time_plan=False):
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
                            self.return_only_from_set, function_for_set=min
                        )
                        df[f"{df_column}_letzter_Tag"] = df[df_column].apply(
                            self.return_only_from_set, function_for_set=max
                        )
                all_floor_levels.append(df)
        print("Files saved successfully")

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
            fig.write_html(os.path.join(path_to_image_folder, "zeitplan.html"))

            # writng xlsx file
            floor_levels_cleaned.to_excel(
                os.path.join(path_to_image_folder, "zeitplan.xlsx"), index=False
            )

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


root = tk.Tk()

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight() - 100
root.geometry(f"{screen_width}x{screen_height}-1+1")

app = Zoom_Advanced(root)

root.mainloop()
