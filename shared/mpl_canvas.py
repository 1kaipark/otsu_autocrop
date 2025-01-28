from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
import matplotlib 
import matplotlib.pyplot as plt 
import numpy as np 




class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, nrows=1, ncols=1, width=5, height=4, **kwargs):
        self.f, self.ax = plt.subplots(nrows, ncols, figsize=(width, height), **kwargs)
        self.no_axes()
        
        super(MplCanvas, self).__init__(self.f)

        if parent:
            self.setParent(parent)

    def no_axes(self):
        # handle removing axes for a single plot or subplots
        if isinstance(self.ax, np.ndarray):
            for a in self.ax.flat:
                a.axis('off')
                self.f.tight_layout()
        else:
            self.ax.axis('off')
            self.f.tight_layout(pad=0.1)

        # self.f.subplots_adjust(top = 1, bottom = 0, right = 1, left = 0, hspace = 0, wspace = 0)

    def refresh(self):
        self.draw_idle()
        self.no_axes()


    def close(self):
        plt.close()

