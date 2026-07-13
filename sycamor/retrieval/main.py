import rasterio as rast
import numpy as np
from matplotlib import pyplot as plt
from rasterio.plot import show, adjust_band
from sycamor.retrieval import dataset, datasetManager, utils, interface
import os
from sycamor.ca import main

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
    

    
def getRadarDataset():
    folder_path = 'data/radar/epsg4326/'

    GRID_CELL = []
    filenames = []
    for f in os.listdir(folder_path):
        if f.endswith('.tiff') and os.path.isfile(os.path.join(folder_path, f)):
            gridCell = f.split('_')[0] +"_" + f.split('_')[1]
            GRID_CELL.append(gridCell )
            filenames.append(f+"")
            
    data = {
        'GRID_CELL': GRID_CELL,
        'EPSG4326Filename': filenames
    }
    geographicDf = pd.DataFrame(data)
    
    folder_path = 'data/radar/hart94/'
      
    GRID_CELL = []
    filenames = []      
    for f in os.listdir(folder_path):
        if f.endswith('.tiff') and os.path.isfile(os.path.join(folder_path, f)):
            gridCell = f.split('_')[0] +"_" + f.split('_')[1]
            GRID_CELL.append(gridCell )
            filenames.append(f+"")
    
    data = {
        'GRID_CELL': GRID_CELL,
        'Hart94Filename': filenames
    }
    projDf = pd.DataFrame(data)        
    
    df = geographicDf.merge(projDf,"left","GRID_CELL")
    print(df)
    return df

def projectToHart94():
    datasetDF = getRadarDataset()
    datasetObj = dataset.Dataset()
    for row in datasetDF.itertuples():
        name = row.EPSG4326Filename.split("_")[0]+"_"+row.EPSG4326Filename.split("_")[1]
        datasetObj.convertToHart94(rast.open("data/radar/epsg4326/"+row.EPSG4326Filename), name)
        
if __name__ == "__main__":
    projectToHart94()