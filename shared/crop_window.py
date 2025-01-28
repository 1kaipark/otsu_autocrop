"""
TODO:
* pad image with a ton of 0's, so text doesn't get cut off
    ／l、         
    （ﾟ､ ｡ ７          
    l  ~ヽ           
    じしf_,)ノ  
"""

from typing import Callable
import matplotlib.patches
import numpy as np

from PySide6 import QtWidgets as qtw, QtGui as qtg, QtCore as qtc

import matplotlib

matplotlib.use("qtagg")


# from img_crop_utils import load_img_array
from .image_crop_utils import (
    load_img_array,
    generate_crop_rects,
    draw_rects,
    xywh_to_cornerpts,
    get_cropped_images,
    rotate_image,
    params as DEFAULT_PARAMS,
)

from .modal import *
from .mpl_canvas import MplCanvas
from shared.logger import log

import cv2 as cv
from cv2.typing import MatLike

from PIL import Image

import os

import gc 


class CroppedImagesView(qtw.QWidget):
    def __init__(self, images: list[np.array], title: str = "", params: dict = DEFAULT_PARAMS) -> None:
        super().__init__()
        self.images = images
        self.title = title

        self.params = params

        self.initUi()

    def initUi(self) -> None:
        if len(self.images) % 3 == 0:
            ncols = min(len(self.images), 3)
            nrows = (len(self.images) + ncols - 1) // ncols
        else:
            ncols = len(self.images)
            nrows = 1

        self.setFixedSize(qtc.QSize(250*ncols, 350*nrows))

        self.canvas = MplCanvas(
            parent=self,
            nrows=nrows,
            ncols=ncols,
            width=12 * len(self.images),
            height=10,
            dpi=100,
        )
        self._draw()

        self.save_button = qtw.QPushButton("save images")
        self.save_button.clicked.connect(self.save_images)

        lt = qtw.QGridLayout()
        lt.addWidget(self.canvas, 0, 0)


        # rotate panel
        rotate_lt = qtw.QHBoxLayout()
        self.rotate_section_input = qtw.QLineEdit()
        self.rotate_section_input.setPlaceholderText("enter section numbers to rotate, separated by commas")
        self.rotate_section_input.setToolTip("leave blank for all")

        self.rotate_90_cw_button = qtw.QPushButton("90° CW")
        self.rotate_90_cw_button.setToolTip("performs 90 degree clockwise rotation on selected sections")
        self.rotate_90_cw_button.clicked.connect(self.rotate_90_cw)

        self.rotate_custom_cw_button = qtw.QPushButton(f"{self.params['deg_rot']}° cw")
        self.rotate_custom_cw_button.setToolTip("performs custom degree clockwise rotation on selected sections")
        self.rotate_custom_cw_button.clicked.connect(self.rotate_custom_cw)

        self.rotate_custom_ccw_button = qtw.QPushButton(f"{self.params['deg_rot']}° ccw")
        self.rotate_custom_ccw_button.setToolTip("performs custom degree counterclockwise rotation on selected sections")
        self.rotate_custom_ccw_button.clicked.connect(self.rotate_custom_ccw)

        rotate_lt.addWidget(self.rotate_custom_ccw_button)
        rotate_lt.addWidget(self.rotate_section_input)
        rotate_lt.addWidget(self.rotate_custom_cw_button)
        rotate_lt.addWidget(self.rotate_90_cw_button)

        # horizontal flip
        hflip_lt = qtw.QHBoxLayout()
        self.hflp_section_input = qtw.QLineEdit()
        self.hflp_section_input.setPlaceholderText("enter section numbers to flip horizontally (or leave blank for all)")
        self.hflp_section_input.setToolTip("leave blank for all")
        
        self.hflip_section_button = qtw.QPushButton("flip horizontal")
        self.hflp_section_input.setToolTip("performs horizontal flip on selected sections")
        self.hflip_section_button.clicked.connect(self.hflip_sections)

        hflip_lt.addWidget(self.hflp_section_input)
        hflip_lt.addWidget(self.hflip_section_button)

        lt.addLayout(rotate_lt, 1, 0)
        lt.addLayout(hflip_lt, 2, 0)
        lt.addWidget(self.save_button, 3, 0)

        self.setLayout(lt)

    def _draw(self) -> None:
        if len(self.images) == 1:
            self.canvas.ax.imshow(self.images[0])
            self.canvas.ax.set_title(f"section_001")
        else:
            for i, ax in enumerate(self.canvas.ax.flat):
                ax.imshow(self.images[i])
                ax.set_title(f"section_{str(i+1).zfill(3)}")  # zfill to pad with zeros
        self.canvas.draw()

    def rotate_90_cw(self) -> None: 
        try:
            idxs = self.rotate_section_input.text()
            log(idxs)
            idxs = idxs.split(",")
            idxs = [int(i.strip()) - 1 for i in idxs]
        except Exception as e:
            log("failed to parse index entry {}".format(self.rotate_section_input.text()))
            idxs = [i for i in range(len(self.images))]

        for i in idxs:
            self.images[i] = cv.rotate(self.images[i], cv.ROTATE_90_CLOCKWISE)
        self._draw()

    def rotate_custom_cw(self) -> None: 
        #         print("rotating 5 degrees clockwise")
        try:
            idxs = self.rotate_section_input.text()
            log(idxs)
            idxs = idxs.split(",")
            idxs = [int(i.strip()) - 1 for i in idxs]
        except Exception as e:
            log("failed to parse index entry {}".format(self.rotate_section_input.text()))
            idxs = [i for i in range(len(self.images))]

        for i in idxs:
            self.images[i] = rotate_image(self.images[i], -1*self.params['deg_rot']) # you would think that negatives are CCW but i can't be bothered to change the implementation xd
        self._draw()

    def rotate_custom_ccw(self) -> None: 
        try:
            idxs = self.rotate_section_input.text()
            log(idxs)
            idxs = idxs.split(",")
            idxs = [int(i.strip()) - 1 for i in idxs]
        except Exception as e:
            log("failed to parse index entry {}".format(self.rotate_section_input.text()))
            idxs = [i for i in range(len(self.images))]

        for i in idxs:
            self.images[i] = rotate_image(self.images[i], self.params['deg_rot'])
        self._draw()

    def hflip_sections(self) -> None:
        try:
            idxs = self.hflp_section_input.text()
            log(idxs)
            idxs = idxs.split(",")
            idxs = [int(i.strip()) - 1 for i in idxs]
        except Exception as e:
            log("failed to parse index entry {}".format(self.hflp_section_input.text()))
            idxs = [i for i in range(len(self.images))]

        for i in idxs:
            self.images[i] = cv.flip(self.images[i], 1) # 1 = horizontal flip
        self._draw() 

    def save_images(self) -> None:
        save_dir = qtw.QFileDialog.getExistingDirectory(
            options=qtw.QFileDialog.Option.ShowDirsOnly
        )
        log(save_dir)

        if save_dir == "":
            info_box(self, "no directory selected, nothing saved")
            return

        # write to disk
        try:
            for i, img in enumerate(self.images):
                fname = os.path.join(
                    save_dir, f"{self.title}_section_{str(i+1 ).zfill(3)}.png"
                )
                img = Image.fromarray(img)
                img.save(fname)
            info_box(self, f"saved {len(self.images)} images to {save_dir}")

        except Exception as e:
            log(str(e))
    
    def closeEvent(self, event):
        self.canvas.close()
        del(self.images)
        del(self.canvas)
        gc.collect()



class CropWindow(qtw.QWidget):
    def __init__(self, image: np.array, title: str = "", params: dict = DEFAULT_PARAMS):
        """
        main crop window, with image display, buttons to apply algorithm and crop sections
        ----

        """
        super().__init__()
        if image.ndim == 3:
            self.image = np.pad(image, pad_width = [(400, 400), (400, 400), (0, 0)], mode='mean') # pad image to avoid overflow, intuitively padding with mean value will work best with Otsu's
        elif image.ndim == 2:
            self.image = np.pad(image, pad_width = [(400, 400), (400, 400)], mode='mean')
        else:
            log("invaild image presented")
            error_box(self, "image.ndim must be 2 or 3", "ermmm")

        self.title = title # our image title (slide name, i.e)
        self.params = params

        # store identified bounding rects here
        self.rects: list[MatLike | None] = []

        # store the actual cropped section images here
        self.cropped_sections: list[np.ndarray | None] = []

        # for drawing, dragging bounding rects
        self.rect = None
        self.start_x = None
        self.start_y = None
        self.bg = None # this will store a buffer of the image for blitting

        # https://stackoverflow.com/questions/72732294/can-i-change-the-rate-at-which-matplotlib-updates-the-motion-notify-event-even
        # only update drawing every n events
        self._n_motion_events = 0

        # for closeEvent
        self.cropped_display = None

        # for pseudo undo redo actions

        self._recently_removed = None

        self.initUi()

    def initUi(self) -> None:
        """draw ui elements"""
        self.setFixedSize(800, 500)
        self.canvas = MplCanvas(parent=self, width=5, height=4, dpi=100)

        # map events for FigureCanvasQTAgg
        # https://matplotlib.org/stable/users/explain/figure/event_handling.html
        # we wanna start drawing rect on mouse down, and append on release
        self.canvas.mpl_connect("button_press_event", self.on_press)
        self.canvas.mpl_connect("motion_notify_event", self.on_motion)
        self.canvas.mpl_connect("button_release_event", self.on_release)

        # display image on the canvas
        self.canvas.ax.imshow(self.image)
        self.canvas.f.suptitle(self.title)

        # initialize the rest of the UI elements
        self.process_button = qtw.QPushButton("process image")
        self.process_button.clicked.connect(self.apply_threshold)

        self.section_input = qtw.QLineEdit()
        self.section_input.setPlaceholderText("enter selected rect indices here...")

        self.select_sections_button = qtw.QPushButton("select sections")
        self.select_sections_button.setToolTip("HELLO")
        self.select_sections_button.clicked.connect(self.open_cropped_display)

        # menu bar to undo, redo
        menubar = qtw.QMenuBar(self)
        edit_menu = menubar.addMenu("edit")

        undo_action = qtg.QAction("undo", self)
        undo_action.setShortcut("Ctrl+Z")
        undo_action.triggered.connect(self.delete_last_rect)

        redo_action = qtg.QAction("redo", self)
        redo_action.setShortcut("Ctrl+Shift+Z")
        redo_action.triggered.connect(self.restore_last_rect)

        edit_menu.addAction(undo_action)
        edit_menu.addAction(redo_action)

        # layouts
        lt = qtw.QGridLayout()
        lt.setMenuBar(menubar)
        lt.addWidget(self.canvas, 1, 0)
        lt.addWidget(self.process_button, 0, 0)

        section_sel = qtw.QHBoxLayout()
        section_sel.addWidget(self.section_input)
        section_sel.addWidget(self.select_sections_button)

        lt.addLayout(section_sel, 2, 0)

        self.setLayout(lt)




    def draw_rects_to_canvas(self) -> None:
        """refreshes canvas with new processed image"""
        image_with_rects = draw_rects(self.image, self.rects, self.params)
        self.canvas.ax.clear()
        self.canvas.ax.imshow(image_with_rects)
        self.canvas.refresh()

    def apply_threshold(self) -> None:
        """generate (x1, y1, x2, y2) coordinates based on algorithmically detected objects, then draw to canvas"""
        log("process button clicked")
        self.rects = generate_crop_rects(self.image, self.params)
        self.draw_rects_to_canvas()

    def open_cropped_display(self) -> None:
        """opens subplots display for cropped sections"""
        log("crop button clicked")
        try:
            idxs = self.section_input.text()
            log(idxs)
            idxs = idxs.split(",")
            idxs = [int(i.strip()) for i in idxs]
        except Exception as e:
            log("failed to parse index entry {}".format(self.section_input.text()))
            idxs = [i for i in range(len(self.rects))]

        try:
            self.cropped_sections = get_cropped_images(self.image, idxs, self.rects)
        except IndexError as e:
            log("invalid index provided: {}".format(str(e)))
            error_box(self, str(e), "failed to crop based on provided index")

        # TODO: code the cropped images display subwindow
        # This subwindow should have a MplCanvas widget with n subplots as columns,
        # a "rotate" button that rotates 90 deg CW, and a "save" button
        self.cropped_display = CroppedImagesView(self.cropped_sections, self.title, self.params)
        self.cropped_display.show()

    def on_press(self, event) -> None:
        """called when mouse is pressed, to initiate drawing a rectangle"""
        # event.inaxes is the Axes instance over which the mouse is -- https://matplotlib.org/stable/users/explain/figure/event_handling.html
        if event.inaxes is not None:
            self.start_x, self.start_y = event.xdata, event.ydata
            self.rect = matplotlib.patches.Rectangle(
                xy=(self.start_x, self.start_y),
                width=0,
                height=0,
                fill=True,
                facecolor="blue",
                alpha=0.2,
            )
            event.inaxes.add_patch(self.rect)
            # self.canvas.blit(self.canvas.ax.bbox)

        # since we're gonna be drawing, save to the buffer now
        self.bg = self.canvas.copy_from_bbox(self.canvas.f.bbox)



    def on_motion(self, event) -> None:
        """continue drawing rectangle for mouse motion"""
        self._n_motion_events += 1
        if self._n_motion_events >= 5:
            self._n_motion_events = 0
        # https://matplotlib.org/stable/users/explain/animations/blitting.html
            # self.canvas.refresh()
            if self.rect is not None and event.inaxes is not None:
                self.canvas.restore_region(self.bg)
                x_init, y_init = self.rect.xy
                self.rect.set_width(event.xdata - x_init)
                self.rect.set_height(event.ydata - y_init)
                self.canvas.f.draw_artist(self.rect)
                self.canvas.blit(self.rect.clipbox)


    def on_release(self, event) -> None:
        """when mouse is released, append rectangle to self.rects"""
        if self.rect is not None:
            # new rect in the form (x1, y1, x2, y2)
            new_rect = (
                self.rect.get_x(),
                self.rect.get_y(),
                self.rect.get_width(),
                self.rect.get_height(),
            )
            new_rect = xywh_to_cornerpts(new_rect)

            # int everything
            new_rect = tuple([int(c) for c in new_rect])
            print(new_rect)
            self.rect = None

            self.rects.append(new_rect)
            self.draw_rects_to_canvas()

            self.bg = None # reset bg buffer

    def delete_last_rect(self) -> None:
        """remove last entry in self.rects and store in buffer"""
        self._recently_removed = self.rects.pop(-1)
        self.draw_rects_to_canvas()

    def restore_last_rect(self) -> None:
        """restore from buffer"""
        if self._recently_removed is not None:
            self.rects.append(self._recently_removed)
            self._recently_removed = None 
            self.draw_rects_to_canvas()


    def closeEvent(self, event) -> None:
        if self.cropped_display:
            self.cropped_display.close()
        self.canvas.close()
        del(self.image)
        del(self.cropped_sections)
        gc.collect()
