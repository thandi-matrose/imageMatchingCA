
import rasterio as rast
import numpy as np

class Grid:
    heightPx: int
    widthPx : int
    

    def __init__(self, image):
        if type(image) == "rasterio.io.DatasetReader":
            self.grid = np.array([image.read(1)],[image.read(2)],[image.read(3)])
            self.heightPx = len(self.grid)
            print(self.heightPx)
            self.widthPx = len(self.grid[0])
            print(self.widthPx)

    # A method to define behavior
    def bark(self):
        return f"{self.name} says Woof!"


    


