import rasterio as rast
import numpy as np
from matplotlib import pyplot as plt
from rasterio.plot import show, adjust_band

class Grid:
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
        
        self.updateGrid = np.empty((self.bands, self.widthPx+sinkSize*2, self.heightPx+sinkSize*2))


        print(self.grid.shape)
        
        

        newRow = np.array([[np.full(self.heightPx, sinkValue, dtype=int)],
                               [np.full(self.heightPx, sinkValue, dtype=int)],
                              [np.full(self.heightPx, sinkValue, dtype=int)]])
        newRow = np.transpose(newRow, axes=(0,1,2))
        self.grid = np.insert(self.grid, 0, newRow, axis=1)
        print(newRow.shape)
        newRow = np.transpose(newRow, axes=(0,1,2))
        self.grid = np.append(self.grid, newRow, axis=1)

        print(newRow.shape)
        print("self shape after row" , self.grid.shape)

        newColumn = np.array([[np.full(self.widthPx + sinkSize*2, sinkValue, dtype=int)],
                               [np.full(self.widthPx + sinkSize*2, sinkValue, dtype=int)],
                              [np.full(self.widthPx+sinkSize*2, sinkValue, dtype=int)]])
        newColumn = np.transpose(newColumn, axes=(0,1,2))
        print("column shape: ", newColumn.shape)
        print("self shape before column" , self.grid.shape)
        self.grid = np.insert(self.grid, 0, newColumn, axis=2)
        newColumn = np.transpose(newColumn, axes=(0,2,1))
        print("column shape" , newColumn.shape)
        print("self shape after column" , self.grid.shape)
        self.grid = np.append(self.grid, newColumn, axis=2)

        print(newColumn.shape)
        print(self.grid[0])
        
        
        #self.grid = np.insert(self.grid, 0, newColumn, axis=1)
        #self.grid = np.append(self.grid, newColumn, axis=1)
        
        

    
def readImage(pathToFile):

    path = "data/"
    print("Reading ", path, pathToFile, "...", sep="")
    src = rast.open(path+pathToFile)
    dimensions = src.shape
    coordRefSystem = src.crs
    print(src.shape)
    print(src.crs)
    grid =  Grid(src)
    print((grid.grid[0][4099]))
    plotImage(src, title=pathToFile)
    return grid

def plotImage(src, title="Image"): 
    band1 = src.read(1)
    print("Dataset Transform:")
    print(src.transform)
    height = band1.shape[0]
    width = band1.shape[1]
    cols, rows = np.meshgrid(np.arange(width), np.arange(height))
    #print(cols, rows)
    xs, ys = rast.transform.xy(src.transform, rows, cols)
    print(xs)
    print(ys)
    pixelRes = np.average(np.diff(xs))*100.0

    print(pixelRes, "cm")
    cols, rows = np.meshgrid(np.arange(width), np.arange(height))
    x, y = src.transform * (rows, cols)

    imgdata = np.array([adjust_band(src.read(i)) for i in (3,2,1)])

    show(imgdata)
    
def main():

    print("Image Matching CA")
    print("-"*25)
    
    
    grid =  readImage("geotiff/Spliced1km_RGB_5cm_W55D_103.TIF")
    print((grid.grid[0][4099]))
    

    
if __name__ == "__main__":
    main()