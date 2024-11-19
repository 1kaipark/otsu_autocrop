# OTSU AUTOCROP
* A graphical user interface (GUI) for supervised automatic cropping of histological slides.

# HOW TO USE
## Install:
* Clone this repository into a directory of your choice and `cd` into it
  ```
  git clone https://github.com/1kaipark/otsu_autocrop.git
  cd otsu_autocrop
  ```
* Install `requirements.txt`
  ```
  pip install -r requirements.txt
  ```
* Run the launcher
```
python otsu_autocrop.py
```
## Loading Slides
* Click "load images", and select all composite slide images.
* Double click to open any image from the tree view. Only one image can be opened at a time. 
* Click "process image" to apply the object detection algorithm.
* If the algorithm fails to detect any sections or regions of interest, you can manually click and drag rectangles.
  * for mistaken entries, there is a pseudo-undo/redo operation that simply removes the latest rectangle.
* Once all regions are identified, input their corresponding indices in the order you wish, from left to right, into the entry field below. Then, click "select sections".
* Once the section view has opened, if desired, rotate or flip sections of your choice. Then, hit "save images" and browse to a directory of your choice to write the images to disk.
* Repeat for remaining images.

# ALGORITHM DETAILS
* Images are first padded with 400 pixels of the mean pixel value to prevent index labels from going off-screen. Then, images are converted to greyscale and are fed through the following pipeline:
  * Gaussian blur for noise reduction
  * Morphological dilation, to fill any gaps or holes, followed by erosion, to restore the original bounds (further noise reduction)
  * Otsu's thresholding algorithm -- in short, thresholds along a single intensity value that maximizes intra-class intensity variance
  * OpenCV2's contour detection, then simplification via a convex hull, and finally a bounding rectangle around each hull
  * The identified rectangles are then sorted by area and the largest 10 are kept.
* `params.json` contains the parameters for various steps in the algorithm that may be important for customization:
  * `blur_kernel_dim`: the size (nxn) of the Gaussian blur kernel
  * `morphological_iterations`: number of iterations for erosion and dilation
  * `morph_kernel_dim`: the size (nxn) of the kernels used for erosion and dilation
  * `thresh`: chosen arbitrarily as a starting point as the Otsu method algorithm finds an ideal value in an unsupervised fashion
  * `pad`: number of pixels to pad each identified rectangle with. For low-contrast images, increasing may help.


# CHANGELOG:
  * 2024-11-15:
    * support for draggable rects from any corner -- no longer just top left
    * uses `blit` for less input lag when drawing rectangles
    * undo and redo

# TODO:
* better handling for overwrites
* expand params
