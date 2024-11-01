from PySide6 import QtWidgets as qtw


def info_box(parent, text: str, title: str = "") -> None:
    info = qtw.QMessageBox(parent)
    info.setText(text)
    info.setWindowTitle(title)

    response = info.exec() # OK button

    if response == qtw.QMessageBox.StandardButton.Ok:
        info.close()


def error_box(parent, text: str, title: str = "") -> None:
    ...

def prompt_yes_no(parent, text: str, title: str = "") -> bool: ...