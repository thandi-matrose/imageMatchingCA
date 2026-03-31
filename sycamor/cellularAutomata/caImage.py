import numpy as np


class CellularAutomatonImage:
    heightPx = 0
    widthPx = 0
    bands = 1
    global sinkValue
    sinkValue = -7
    global sinkSize
    sinkSize = 2

    def __init__(self, image):
        self.grid = np.array([image.read(1),image.read(2),image.read(3)])
        print(self.grid)
        self.bands = len(self.grid)
        self.widthPx = len(self.grid[0])
        self.heightPx = len(self.grid[0][0])
        
        
        
       