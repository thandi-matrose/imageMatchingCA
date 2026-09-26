import os

import rasterio as rast
import numpy as np
from matplotlib import pyplot as plt
from rasterio.plot import show, adjust_band
from sycamor.retrieval import dataset

import geopandas as gpd
import pandas as pd

from sycamor.visualisation.plot import plotRGBImage
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
    grid =  main.CellularAutomatonImage(src)
    print((grid.grid[0][4095]))
    plotRGBImage(src, title=pathToFile)
    return grid

def main():
    pass
    

    


def projectToHart94():
    datasetDF = dataset.getRadarDataset()
    datasetObj = dataset.Dataset()
    for row in datasetDF.itertuples():
        name = row.EPSG4326Filename.split("_")[0]+"_"+row.EPSG4326Filename.split("_")[1]
        datasetObj.convertToHart94(rast.open("data/radar/epsg4326/"+row.EPSG4326Filename), name)
        
if __name__ == "__main__":
    projectToHart94()