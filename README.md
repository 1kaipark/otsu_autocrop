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
  * Start from the **top-left corner**, click and drag the new rectangle to the bottom right corner. Due to the use of `matplotlib` here, the input lag is high and you have to be deliberate with your inputs.
* Once all regions are identified, input their corresponding indices in the order you wish, from left to right, into the entry field below. Then, click "select sections".
* Once the section view has opened, if desired, click "rotate" for a 90-degree clockwise rotation. Then, hit "save images" and browse to a directory of your choice to write the images to disk.
* Repeat for remaining images.


# TODO:
* show saved files in file dialog, have better handling for overwrites
* not implemented:
  * settings panel for editing params.json (you can do this manually if need be)
