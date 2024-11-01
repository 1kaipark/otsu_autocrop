from shared.crop_window import CropWindow
from shared.image_crop_utils import load_img_array
from shared.modal import *

import sys
from PySide6 import QtWidgets as qtw, QtCore as qtc, QtGui as qtg
import json

import numpy as np

from pathlib import Path

import matplotlib
matplotlib.use("QtAgg")


class AutocropFileViewer(qtw.QWidget):
    def __init__(self) -> None:
        super().__init__()

        self.image_paths: list[str | None] = []
        self.stitched_images: list[np.array | None] = []

        with open("params.json", "r") as h:
            self.params = json.load(h)

        self.initUi()

        # for closeEvent
        self.settings_panel = None
        self.crop_window = None

    def initUi(self) -> None:
        self.setFixedSize(qtc.QSize(400, 200))

        self.tree = qtw.QTreeWidget()
        self.tree.setColumnCount(2)
        self.tree.setHeaderLabels(["image", "viewed"])

        self.tree.itemDoubleClicked.connect(
            self.on_item_click
        )  # this should open the crop window

        self.load_images_button = qtw.QPushButton("load images")
        self.load_images_button.clicked.connect(self.load_images)

        self.clear_images_button = qtw.QPushButton("clear images")
        self.clear_images_button.clicked.connect(self.clear_images)

        lt = qtw.QVBoxLayout()
        lt.addWidget(self.tree)
        
        btns_lt = qtw.QHBoxLayout()
        btns_lt.addWidget(self.load_images_button)
        btns_lt.addWidget(self.clear_images_button)
        
        lt.addLayout(btns_lt)
        self.setLayout(lt)

        menubar = qtw.QMenuBar(self)
        file_menu = qtw.QMenu("file", self)

        open_settings_action = qtg.QAction("settings", self)
        open_settings_action.triggered.connect(self.open_settings)
        file_menu.addAction(open_settings_action)

        exit_action = qtg.QAction("exit", self)
        exit_action.triggered.connect(qtw.QApplication.instance().quit)
        file_menu.addAction(exit_action)

        menubar.addMenu(file_menu)
        lt.setMenuBar(menubar)

    def on_item_click(self, item: qtw.QTreeWidgetItem, column: int) -> None: 
        image_path = item.data(0, qtc.Qt.UserRole)
        if image_path:
            item.setText(1, "yes")
            image = load_img_array(image_path)
            self.crop_window = CropWindow(image, item.text(0), self.params)
            self.crop_window.show()

    def load_images(self) -> None:
        self.image_paths, _ = qtw.QFileDialog.getOpenFileNames(
            self, "select slide images", "", "images (*.jpg *.png, *.tif)"
        )
        print(self.image_paths)
        for image_path in self.image_paths:
            image_name = Path(image_path).stem.strip()

            try:
                item = qtw.QTreeWidgetItem([image_name, "no"])
                item.setData(0, qtc.Qt.UserRole, image_path)
                self.tree.addTopLevelItem(item)
            except Exception as e:
                info_box(self, "error: {}".format(str(e)))
    def clear_images(self) -> None:
        # modal to confirm??
        ...

    def open_settings(self) -> None: ...

    def closeEvent(self, event) -> None:
        if self.crop_window:
            self.crop_window.close()


if __name__ == "__main__":
    app = qtw.QApplication(sys.argv)
    w = AutocropFileViewer()
    w.show()
    sys.exit(app.exec())
