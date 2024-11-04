import matplotlib.pyplot as plt
import numpy as np
import cv2 as cv

def ColorGenerator():
    colors: list[tuple[int, int, int]] = [
        (255, 255, 255),
        (0, 255, 255),
        (255, 0, 255),
        (255, 255, 0),
        (0, 0, 255),
        (0, 255, 0),
        (255, 0, 0),
    ]
    count = 0
    while count < len(colors):
        yield colors[count]
        count += 1
        count = count % len(colors)  # this is swag

