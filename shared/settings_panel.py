from .image_crop_utils import params as DEFAULT_PARAMS
from .modal import info_box
import os
from PySide6 import QtWidgets as qtw, QtCore as qtc, QtGui as qtg
import json

from typing import Callable

class SettingsPanel(qtw.QWidget):
    def __init__(self, cfg_path: str, refresh_command: Callable | None = None) -> None:
        """
        QWidget for the settings panel. This is just a graphical interface for params.json
        ----
        specify `refresh_command` to have the main window refresh its settings
        """
        super().__init__()
        self.cfg_path = cfg_path
        self.cfg: dict = DEFAULT_PARAMS
        if os.path.exists(self.cfg_path):
            with open(self.cfg_path, 'rb') as h:
                self.cfg = json.load(h)

        self.refresh_command = refresh_command

        self.initUi()



    def initUi(self) -> None:
        """basically a graphical display of params.json. the key:value pairs are NOT FIXED"""
        self.setFixedSize(qtc.QSize(300, 50*len(self.cfg.keys())))
        lt = qtw.QGridLayout()

        # store key:value label:entry pairs in this dict
        self.labels_entries: dict = {}
        for i, key in enumerate(self.cfg.keys()):
            label = qtw.QLabel(key)
            entry = qtw.QLineEdit()

            entry.setText(str(self.cfg[key]))

            lt.addWidget(label, i, 0)
            lt.addWidget(entry, i, 1)

            self.labels_entries[label] = entry

        self.save_button = qtw.QPushButton("save config")
        self.save_button.clicked.connect(self.save_config)
        lt.addWidget(self.save_button, i+1, 1)

        self.setLayout(lt)
    
    def save_config(self) -> None: 
        new_cfg: dict = {
            label.text(): int(entry.text()) for label, entry in self.labels_entries.items()
        } # parse widgets to create new dict 

        with open(self.cfg_path, 'w') as h:
            json.dump(new_cfg, h) # dump to json
        
        if self.refresh_command:
            self.refresh_command()

        info_box(self, "saved to params.json")
        self.close()

        

