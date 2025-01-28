
from PySide6 import QtWidgets as qtw, QtCore as qtc
from PySide6.QtGui import QIcon
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
import cv2

from shared.mpl_canvas import MplCanvas


# TODO: add file menu for opening images 
# TODO: add "attempt autorotate" button with alg
# maybe a treeview like the autocrop program?

class BatchRotator(qtw.QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Image Batch Rotator")
        self.setGeometry(100, 100, 800, 600)

        # Main layout
        layout = qtw.QVBoxLayout(self)

        # Top navigation bar
        nav_layout = qtw.QHBoxLayout()
        self.prev_button = qtw.QPushButton("< Prev")
        self.next_button = qtw.QPushButton("Next >")
        self.current_img_label = qtw.QLabel("CURRENT_IMG")
        self.current_img_label.setAlignment(qtc.Qt.AlignCenter)

        nav_layout.addWidget(self.prev_button)
        nav_layout.addWidget(self.current_img_label)
        nav_layout.addWidget(self.next_button)

        layout.addLayout(nav_layout)

        # Image display area
        self.canvas = MplCanvas(self)
        layout.addWidget(self.canvas)

        # Bottom rotation bar
        rot_layout = qtw.QHBoxLayout()
        self.rot_ccw_button = qtw.QPushButton("Rotate 5° CCW")
        self.rot_cw_button = qtw.QPushButton("Rotate 5° CW")
        rot_layout.addWidget(self.rot_ccw_button)
        rot_layout.addWidget(self.rot_cw_button)

        layout.addLayout(rot_layout)

        # Connect buttons to functions
        self.prev_button.clicked.connect(self.show_prev_image)
        self.next_button.clicked.connect(self.show_next_image)
        self.rot_ccw_button.clicked.connect(self.rotate_ccw)
        self.rot_cw_button.clicked.connect(self.rotate_cw)

        # Dummy image list
        self.image_paths = ["image1.jpg", "image2.jpg", "image3.jpg"]
        self.current_index = 0
        self.load_image(self.image_paths[self.current_index])

    def load_image(self, path):
        """Loads and displays an image on the MplCanvas."""
        img = cv2.imread(path)
        if img is not None:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            self.canvas.ax.clear()
            self.canvas.ax.imshow(img)
            self.canvas.refresh()

    def show_prev_image(self):
        self.current_index = (self.current_index - 1) % len(self.image_paths)
        self.current_img_label.setText(self.image_paths[self.current_index])
        self.load_image(self.image_paths[self.current_index])

    def show_next_image(self):
        self.current_index = (self.current_index + 1) % len(self.image_paths)
        self.current_img_label.setText(self.image_paths[self.current_index])
        self.load_image(self.image_paths[self.current_index])

    def rotate_ccw(self):
        """Rotate the current image 5 degrees counter-clockwise."""
        self.rotate_image(-5)

    def rotate_cw(self):
        """Rotate the current image 5 degrees clockwise."""
        self.rotate_image(5)

    def rotate_image(self, angle):
        img = cv2.imread(self.image_paths[self.current_index])
        if img is not None:
            img_center = tuple(np.array(img.shape[1::-1]) / 2)
            rot_mat = cv2.getRotationMatrix2D(img_center, angle, 1.0)
            rotated_img = cv2.warpAffine(img, rot_mat, img.shape[1::-1], flags=cv2.INTER_LINEAR)
            rotated_img = cv2.cvtColor(rotated_img, cv2.COLOR_BGR2RGB)

            self.canvas.ax.clear()
            self.canvas.ax.imshow(rotated_img)
            self.canvas.refresh()


# Main loop
if __name__ == "__main__":
    app = qtw.QApplication([])
    rotator = BatchRotator()
    rotator.show()
    app.exec()