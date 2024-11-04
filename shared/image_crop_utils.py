from typing import Iterable
import cv2 as cv
import numpy as np
from PIL import Image

from cv2.typing import MatLike, Rect

from .colors import ColorGenerator

params: dict = {
    "blur_kernel_dim": 7,
    "morphological_iterations": 8,
    "morph_kernel_dim": 6,
    "thresh": 0,
    "pad": 50,
}

# This will convert rects of the form (x, y, w, h) to (x1, y1, x2, y2)
xywh_to_cornerpts = lambda rect: (
    rect[0],
    rect[1],
    (rect[0] + rect[2]),
    (rect[1] + rect[3]),
)

pad_rect = lambda rect, pad: (
    rect[0] - pad,
    rect[1] - pad,
    rect[2] + pad,
    rect[3] + pad,
)


def load_img_array(ipath: str) -> np.ndarray:
    """load image path as ndarray"""
    return np.asarray(Image.open(ipath))  # use PIL to open, then return the array


# wrapper functions
def erode(img: np.ndarray, iterations: int = 2, kernel_size: int = 3) -> np.ndarray:
    """applies erosion according to the specified parameters"""
    kernel = np.ones((kernel_size, kernel_size), np.uint8)
    img = cv.erode(img, kernel, iterations=iterations, anchor=(1, 1))
    return img


def dilate(img: np.ndarray, iterations: int = 2, kernel_size: int = 3) -> np.ndarray:
    """applies erosion according to the specified parameters"""
    kernel = np.ones((kernel_size, kernel_size), np.uint8)
    img = cv.dilate(img, kernel, iterations=iterations, anchor=(1, 1))
    return img


def generate_crop_rects(image: np.ndarray, params: dict = params) -> list["MatLike"]:
    blank: np.ndarray = image.copy()
    image = cv.cvtColor(image, cv.COLOR_RGB2GRAY)
    image = cv.GaussianBlur(
        image, ksize=(params["blur_kernel_dim"], params["blur_kernel_dim"]), sigmaX=0
    )

    # dilation to fill in holes, then erosion to restore the original bounds
    image = dilate(
        image,
        iterations=params["morphological_iterations"],
        kernel_size=params["morph_kernel_dim"],
    )
    image = erode(
        image,
        iterations=params["morphological_iterations"],
        kernel_size=params["morph_kernel_dim"],
    )

    # to this day I have no idea what the first item cv.threshold returns is
    _, thresh = cv.threshold(image, params["thresh"], 255, cv.THRESH_OTSU)

    # hierarchy might be useful at some point but not now
    contours, _ = cv.findContours(thresh, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)

    # take the 10 largest contours -- never gonna have more than 10 sections per slide
    contours = sorted(contours, key=cv.contourArea, reverse=True)[:params["n_sections"]]
    # I love list comprehension
    hulls: list["MatLike"] = [cv.convexHull(c) for c in contours]

    rects: list["Rect"] = [cv.boundingRect(c) for c in contours]
    rects = [xywh_to_cornerpts(rect) for rect in rects]
    rects = [pad_rect(rect, params['pad']) for rect in rects]
    # doing inline returns gives me bad vibes tbh
    return rects


def draw_rects(src: np.ndarray, rects: list[tuple[int, int, int, int]], params: dict):
    """this method should take a source image and superimpose rects with their corresponding indices onto it"""
    bg = src.copy()  # for read only
    cg = ColorGenerator() # yields colors

    for i, rect in enumerate(rects):
        color = next(iter(cg))
        cv.rectangle(
            img=bg,
            pt1=(rect[0], rect[1]),
            pt2=(rect[2], rect[3]),
            color=color,
            thickness=4,
            lineType=cv.LINE_AA,
        )

        cv.putText(
            img=bg,
            text=f"{i}",
            org=(rect[0] - 10, rect[1] - 10),
            fontFace=cv.FONT_ITALIC,
            fontScale=5,
            color=color,
            thickness=5,
            lineType=2,
        )

    return bg


def crop_rect(image: np.array, rect: tuple[int, int, int, int]) -> np.array:
    x1, y1, x2, y2 = rect
    img_crop = image[y1:y2, x1:x2]

    return img_crop


def get_cropped_images(
    src: np.ndarray,
    idxs: list[int],
    rects: list[tuple[int, int, int, int]],
) -> list[np.ndarray]:
    """provided a list of indices and bounding rects, crop the source image"""
    selected = [rects[n] for n in idxs]
    cropped = [crop_rect(src, rect) for rect in selected]
    return cropped
