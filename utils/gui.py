# -*- coding: utf-8 -*-
# Advanced zoom example. Like in Google Maps.
# It zooms only a tile, but not the whole image. So the zoomed tile occupies
# constant memory and not crams it with a huge resized image for the large zooms.

import tkinter as tk
import tkinter.font as tk_font
from tkinter import ttk
from PIL import Image, ImageTk


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
        button_font = tk_font.Font(size=20)

        # add buttons on the right
        frame_right = tk.Frame(master=self.master)
        self.buttonA = tk.Button(master=frame_right, padx=3, pady=3, text="Button A")
        self.buttonB = tk.Button(master=frame_right, padx=3, pady=3, text="Button B")
        self.buttonC = tk.Button(master=frame_right, padx=3, pady=3, text="Button C")
        self.buttonD = tk.Button(master=frame_right, padx=3, pady=3, text="Button D")
        self.buttonE = tk.Button(master=frame_right, padx=3, pady=3, text="Button E")
        self.buttonA["font"] = button_font
        self.buttonB["font"] = button_font
        self.buttonC["font"] = button_font
        self.buttonD["font"] = button_font
        self.buttonE["font"] = button_font
        self.buttonA.grid(row=0, column=0, sticky="nswe", padx=5, pady=5)
        self.buttonB.grid(row=1, column=0, sticky="nswe", padx=5, pady=5)
        self.buttonC.grid(row=2, column=0, sticky="nswe", padx=5, pady=5)
        self.buttonD.grid(row=3, column=0, sticky="nswe", padx=5, pady=5)
        self.buttonE.grid(row=4, column=0, sticky="nswe", padx=5, pady=5)

        frame_right.grid(row=0, column=2, sticky="nswe", padx=10, pady=10)

        # add buttons on the left
        frame_left = tk.Frame(master=self.master)
        self.buttonA = tk.Button(master=frame_left, padx=3, pady=3, text="Button A")
        self.buttonB = tk.Button(master=frame_left, padx=3, pady=3, text="Button B")
        self.buttonC = tk.Button(master=frame_left, padx=3, pady=3, text="Button C")
        self.buttonD = tk.Button(master=frame_left, padx=3, pady=3, text="Button D")
        self.buttonE = tk.Button(master=frame_left, padx=3, pady=3, text="Button E")
        self.buttonA["font"] = button_font
        self.buttonB["font"] = button_font
        self.buttonC["font"] = button_font
        self.buttonD["font"] = button_font
        self.buttonE["font"] = button_font
        self.buttonA.grid(row=0, column=0, sticky="nswe", padx=5, pady=5)
        self.buttonB.grid(row=1, column=0, sticky="nswe", padx=5, pady=5)
        self.buttonC.grid(row=2, column=0, sticky="nswe", padx=5, pady=5)
        self.buttonD.grid(row=3, column=0, sticky="nswe", padx=5, pady=5)
        self.buttonE.grid(row=4, column=0, sticky="nswe", padx=5, pady=5)

        frame_left.grid(row=0, column=0, sticky="nswe", padx=10, pady=10)

        # add buttons on the bottom
        frame_bottom = tk.Frame(master=self.master)
        self.buttonA = tk.Button(master=frame_bottom, padx=3, pady=3, text="Button A")
        self.buttonB = tk.Button(master=frame_bottom, padx=3, pady=3, text="Button B")
        self.buttonC = tk.Button(master=frame_bottom, padx=3, pady=3, text="Button C")
        self.buttonD = tk.Button(master=frame_bottom, padx=3, pady=3, text="Button D")
        self.buttonE = tk.Button(master=frame_bottom, padx=3, pady=3, text="Button E")
        self.buttonA["font"] = button_font
        self.buttonB["font"] = button_font
        self.buttonC["font"] = button_font
        self.buttonD["font"] = button_font
        self.buttonE["font"] = button_font
        self.buttonA.grid(row=0, column=0, sticky="nswe", padx=5, pady=5)
        self.buttonB.grid(row=0, column=1, sticky="nswe", padx=5, pady=5)
        self.buttonC.grid(row=0, column=2, sticky="nswe", padx=5, pady=5)
        self.buttonD.grid(row=0, column=3, sticky="nswe", padx=5, pady=5)
        self.buttonE.grid(row=0, column=4, sticky="nswe", padx=5, pady=5)

        frame_bottom.grid(
            row=1, column=0, columnspan=3, sticky="nswe", padx=10, pady=10
        )

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
            bbox[0] < x < bbox[2]
            and bbox[1] < y < bbox[3]
            and bbox[0] < x + self.rect_scale * self.box_size < bbox[2]
            and bbox[1] < y + self.rect_scale * self.box_size < bbox[3]
        ):
            pass  # Ok! Inside the image
        else:
            return
        tag_x = int(1000 * (x - bbox[0]) / (bbox[2] - bbox[0]))
        tag_y = int(1000 * (y - bbox[1]) / (bbox[3] - bbox[1]))
        self.canvas.create_rectangle(
            x,
            y,
            x + self.rect_scale * self.box_size,
            y + self.rect_scale * self.box_size,
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

# rahmen_side_buttons_left = tk.Frame(master=root)
# buttonB = tk.Button(master=rahmen_side_buttons_left, text="Button B")
# rahmen_buttons_bottom = tk.Frame(master=root)
# buttonC = tk.Button(master=rahmen_buttons_bottom, text="Button C")

# buttonB.grid(column=2, row=0)
# buttonC.grid(column=1, row=1)

root.mainloop()
