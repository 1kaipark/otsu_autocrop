"""
Contains methods to show dialog boxes using QtWidgets.QMessageBox
"""

from PySide6 import QtWidgets as qtw


def info_box(parent, text: str, title: str = "") -> None:
    """regular message box with button 'ok'"""
    info = qtw.QMessageBox(parent)
    info.setText(text)
    info.setWindowTitle(title)

    response = info.exec() # OK button

    if response == qtw.QMessageBox.StandardButton.Ok:
        info.close()


def error_box(parent, text: str, title: str = "") -> None:
    """show an error box, with button 'ok'"""
    error = qtw.QMessageBox()
    # error.setIcon(qtw.QMessageBox.critical())
    error.setText(text)
    error.setWindowTitle(title)

    response = error.exec()

    if response == qtw.QMessageBox.StandardButton.Ok:
        error.close()

def prompt_yes_no(parent, text: str, title: str = "") -> bool:
    """prompt box with options 'yes' or 'no', returns bool value based on user choice"""
    prompt = qtw.QMessageBox(parent)
    prompt.setText(text)
    prompt.setWindowTitle(title)

    prompt.setStandardButtons(qtw.QMessageBox.StandardButton.Yes | qtw.QMessageBox.StandardButton.No)

    response = prompt.exec()

    return response == qtw.QMessageBox.StandardButton.Yes