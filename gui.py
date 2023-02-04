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

    def __init__(self, mainframe, path):
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
        self.shift_x = None
        self.shift_y = None
        self.drawing_direction = None  # can be horizontal or vertical
        self.active_tact_for_planing = f"{TACT_PART} 1"

        self.current_day = pd.Timestamp(datetime.date.today())

        # Functions for buttons
        def blank_function():
            pass

        def change_mode():
            self.drawing_mode_id = (self.drawing_mode_id + 1) % len(
                self.drawing_mode_frames
            )
            current_mode = list(self.drawing_mode_frames)[self.drawing_mode_id]
            for the_frame in self.drawing_mode_frames[current_mode]:
                the_frame.tkraise()

        # Navigation menu on the right (tact and plan)
        self.right_frame_tact_and_plan = tk.Frame(master=self.master)

        # Buttons for the navigation menu on the right (tact and plan)
        self.next_floor_tact_and_plan = tk.Button(
            master=self.right_frame_tact_and_plan,
            padx=3,
            pady=3,
            text=NEXT_FLOOR,
            command=blank_function,
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
            command=blank_function,
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
            command=blank_function,
            bg=all_colors[f"{TACT_PART} 1"],
        )
        self.tact_1_tact_and_plan["font"] = button_font
        self.tact_1_tact_and_plan.grid(row=2, column=0, sticky="nswe", padx=5, pady=5)

        self.tact_2_tact_and_plan = tk.Button(
            master=self.right_frame_tact_and_plan,
            padx=3,
            pady=3,
            text=f"{TACT_PART} 2",
            command=blank_function,
            bg=all_colors[f"{TACT_PART} 2"],
        )
        self.tact_2_tact_and_plan["font"] = button_font
        self.tact_2_tact_and_plan.grid(row=3, column=0, sticky="nswe", padx=5, pady=5)

        self.tact_3_tact_and_plan = tk.Button(
            master=self.right_frame_tact_and_plan,
            padx=3,
            pady=3,
            text=f"{TACT_PART} 3",
            command=blank_function,
            bg=all_colors[f"{TACT_PART} 3"],
        )
        self.tact_3_tact_and_plan["font"] = button_font
        self.tact_3_tact_and_plan.grid(row=4, column=0, sticky="nswe", padx=5, pady=5)

        self.tact_4_tact_and_plan = tk.Button(
            master=self.right_frame_tact_and_plan,
            padx=3,
            pady=3,
            text=f"{TACT_PART} 4",
            command=blank_function,
            bg=all_colors[f"{TACT_PART} 4"],
        )
        self.tact_4_tact_and_plan["font"] = button_font
        self.tact_4_tact_and_plan.grid(row=5, column=0, sticky="nswe", padx=5, pady=5)

        self.tact_5_tact_and_plan = tk.Button(
            master=self.right_frame_tact_and_plan,
            padx=3,
            pady=3,
            text=f"{TACT_PART} 5",
            command=blank_function,
            bg=all_colors[f"{TACT_PART} 5"],
        )
        self.tact_5_tact_and_plan["font"] = button_font
        self.tact_5_tact_and_plan.grid(row=6, column=0, sticky="nswe", padx=5, pady=5)

        self.tact_6_tact_and_plan = tk.Button(
            master=self.right_frame_tact_and_plan,
            padx=3,
            pady=3,
            text=f"{TACT_PART} 6",
            command=blank_function,
            bg=all_colors[f"{TACT_PART} 6"],
        )
        self.tact_6_tact_and_plan["font"] = button_font
        self.tact_6_tact_and_plan.grid(row=7, column=0, sticky="nswe", padx=5, pady=5)

        self.no_tact_tact_and_plan = tk.Button(
            master=self.right_frame_tact_and_plan,
            padx=3,
            pady=3,
            text=NO_TACT,
            command=blank_function,
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
            command=blank_function,
            bg=all_colors[NEXT_FLOOR],
        )
        self.next_floor_draw["font"] = button_font
        self.next_floor_draw.grid(row=0, column=0, sticky="nswe", padx=5, pady=5)

        self.previous_floor_draw = tk.Button(
            master=self.right_frame_draw,
            padx=3,
            pady=3,
            text=PREVIOUS_FLOOR,
            command=blank_function,
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

        self.cursor_bigger = tk.Button(
            master=self.left_frame,
            padx=3,
            pady=3,
            text=BIGGER,
            command=blank_function,
            bg=all_colors[BIGGER],
        )
        self.cursor_bigger["font"] = button_font
        self.cursor_bigger.grid(row=1, column=0, sticky="nswe", padx=5, pady=5)

        self.cursor_smaller = tk.Button(
            master=self.left_frame,
            padx=3,
            pady=3,
            text=SMALLER,
            command=blank_function,
            bg=all_colors[SMALLER],
        )
        self.cursor_smaller["font"] = button_font
        self.cursor_smaller.grid(row=2, column=0, sticky="nswe", padx=5, pady=5)

        self.save_button = tk.Button(
            master=self.left_frame,
            padx=3,
            pady=3,
            text=SAVE,
            command=blank_function,
            bg=all_colors[SAVE],
        )
        self.save_button["font"] = button_font
        self.save_button.grid(row=3, column=0, sticky="nswe", padx=5, pady=5)

        self.print_button = tk.Button(
            master=self.left_frame,
            padx=3,
            pady=3,
            text=PRINT,
            command=blank_function,
            bg=all_colors[PRINT],
        )
        self.print_button["font"] = button_font
        self.print_button.grid(row=4, column=0, sticky="nswe", padx=5, pady=5)

        # Placing all the buttons on main frame (tact, plan and draw)
        self.left_frame.grid(row=0, column=0, sticky="nswe", padx=10, pady=10)

        # Navigation menu on the bottom (tact)
        self.bottom_frame_tact = tk.Frame(master=self.master)

        # Placing all the buttons on main frame (tact)
        self.bottom_frame_tact.grid(
            row=1, column=0, sticky="nswe", padx=10, pady=10, columnspan=3
        )

        # Navigation menu on the bottom (plan)
        self.bottom_frame_plan = tk.Frame(master=self.master)

        # Buttons for the navigation menu on the bottom (plan)
        self.last_date = tk.Button(
            master=self.bottom_frame_plan,
            padx=3,
            pady=3,
            text=LAST_DAY,
            command=blank_function,
            bg=all_colors[LAST_DAY],
        )
        self.last_date["font"] = button_font
        self.last_date.grid(row=0, column=0, sticky="nswe", padx=5, pady=5)

        self.next_date = tk.Button(
            master=self.bottom_frame_plan,
            padx=3,
            pady=3,
            text=NEXT_DAY,
            command=blank_function,
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
            row=1, column=0, sticky="nswe", padx=10, pady=10, columnspan=3
        )

        # Navigation menu on the bottom (draw)
        self.bottom_frame_draw = tk.Frame(master=self.master)

        self.concrete = tk.Button(
            master=self.bottom_frame_draw,
            padx=3,
            pady=3,
            text=CONCRETE,
            command=blank_function,
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
            command=blank_function,
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
            command=blank_function,
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
            row=1, column=0, sticky="nswe", padx=10, pady=10, columnspan=3
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

        self.image = Image.open(path)  # open image
        self.width, self.height = self.image.size
        self.imscale = 1.0  # scale for the canvas image
        self.delta = 1.3  # zoom magnitude
        # Put image into container rectangle and use it to set proper coordinates to the image
        self.container = self.canvas.create_rectangle(
            0, 0, self.width, self.height, width=0
        )
        self.show_image()
        self.rect_scale = 1
        self.box_size = 5
        self.x_initial = 0
        self.y_initial = 0
        self.x_correction = 0
        self.y_correction = 0
        self.all_rects = set()
        change_mode()

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

    def draw_rect(self, event=None):
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
        tag_x = int(1000 * (x - bbox[0]) / (bbox[2] - bbox[0]))
        tag_y = int(1000 * (y - bbox[1]) / (bbox[3] - bbox[1]))
        self.canvas.create_rectangle(
            x - self.rect_scale * self.box_size / 2,
            y - self.rect_scale * self.box_size / 2,
            x + self.rect_scale * self.box_size / 2,
            y + self.rect_scale * self.box_size / 2,
            fill="black",
            tags=f"{tag_x}-{tag_y}",
        )
        self.all_rects.add(f"{tag_x}-{tag_y}")

    def delete_rect(self, event=None):
        x, y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
        bbox = self.canvas.bbox(self.container)
        tag_x = int(1000 * (x - bbox[0]) / (bbox[2] - bbox[0]))
        tag_y = int(1000 * (y - bbox[1]) / (bbox[3] - bbox[1]))
        for i in range(5):
            for j in range(5):
                self.canvas.delete(f"{tag_x+i}-{tag_y+j}")
                self.all_rects.discard(f"{tag_x+i}-{tag_y+j}")

        if event.char == "d":
            self.canvas.delete("square")


path = r"C:\Users\Vladi\Downloads\norway.jpg"  # place path to your image here
# path = r'C:\Users\dmitrenkovla\Desktop\S21\GTP - Bezeichnung Bauaufzüge.jpg'
root = tk.Tk()

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight() - 100
root.geometry(f"{screen_width}x{screen_height}-1+1")

app = Zoom_Advanced(root, path=path)

root.mainloop()
