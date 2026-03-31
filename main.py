import rasterio as rast
import numpy as np
from matplotlib import pyplot as plt
from rasterio.plot import show, adjust_band
from dataretrieval.woodstocksaltriver import datasetManager
from dataretrieval.sentinelone import interface, utils
import os
from sycamor.cellularAutomata import caImage

new_dir = "/home/thandi/HONOURS/imageMatchingCA" 
os.chdir(new_dir)
print(f"Changed directory to: {os.getcwd()}")
    
def readImage(pathToFile):

    path = "data/geotiff/"
    print("Reading ", path, pathToFile, "...", sep="")
    src = rast.open(path+pathToFile)
    dimensions = src.shape
    coordRefSystem = src.crs
    print(src.bounds)
    print(src.shape)
    print(type(src.crs))
    grid =  caImage.CellularAutomatonImage(src)
    print((grid.grid[0][4095]))
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
    xsRawDiff = np.diff(xs)
    mask = np.ones(xsRawDiff.size, dtype=bool)

    # Set the elements at every nth index (starting from index n-1) to False
    mask[width-1::width] = False 
    xsDiff = xsRawDiff[mask]
    # Apply the mask to 
    pixelRes = np.average(xsDiff)

    print(pixelRes, "m")

    ys_2d = (ys.reshape(width, height).T).flatten()

    ysRawDiff = np.diff(ys_2d)
    mask = np.ones(ysRawDiff.size, dtype=bool)

    # Set the elements at every nth index (starting from index n-1) to False
    mask[height-1::height] = False 
    ysDiff = ysRawDiff[mask]
    # Apply the mask to 
    pixelRes = np.average(ysDiff)

    print(pixelRes, "m")


    cols, rows = np.meshgrid(np.arange(width), np.arange(height))
    x, y = src.transform * (rows, cols)

    imgdata = np.array([adjust_band(src.read(i)) for i in (3,2,1)])
    plt.title(title)
    show(imgdata)

def main():

    print("Image Matching CA")
    print("-"*25)
    hub = interface.SentinelHub()
    aerialDataManager = datasetManager.DatasetManager()
    
  

    studyArea = datasetManager.StudyArea()
    boundingBox = studyArea.getBounds(epsg=utils.EPSG)
    request = hub.createRequest(boundingBox=boundingBox)
    data = hub.sendRequest(request)
    
    print("Encoding" + str(data.apparent_encoding))
    print("Content:" + str(data.content))
    print("Headers:" + str(data.headers))
    print("Content:" + str(data.status_code))
    
    #grid =  readImage("Spliced1km_RGB_5cm_W55D_103.TIF")

    #print((grid.grid[0][4000]))
    

    
if __name__ == "__main__":
    main()