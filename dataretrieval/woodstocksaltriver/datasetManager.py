import os
from typing import Optional
import numpy as np
import rasterio as rast
import fiona


from dataretrieval.sentinelone.utils import EPSG
from sycamor.cellularAutomata import caImage
import geopandas as gpd

class DatasetManager:
    

    def __init__(self):
         pass

    def readImage(self, pathToFile):
        path = "data/geotiff/"
        print("Reading ", path, pathToFile, "...", sep="")
        src = rast.open(path+pathToFile)
        dimensions = src.shape
        coordRefSystem = src.crs
        print(src.bounds)
        print(src.shape)
        print(src.crs)
        grid = caImage.CellularAutomatonImage(src)
        print((grid.grid[0][4095]))
        self.plotImage(src, title=pathToFile)
        return grid
    def plotImage(source, title):
        pass

   
class StudyArea:
    def __init__(self):
            # Reading the shapefile into a GeoDataFrame
            self.studyArea = gpd.read_file("dataretrieval/woodstocksaltriver/studyarea/Official_Planning_Suburbs.shp")
            #self.studyArea = gpd.read_file("dataretrieval/woodstocksaltriver/studyarea/NOT/Official_Suburb.shp")
            
            
            # Displaying the first few rows and metadata
            print(self.studyArea.to_records())
            print(self.studyArea.head())
            print(self.studyArea.crs)

    def getBounds(self, epsg = None):    
        
        gdf = self.studyArea
        if epsg is not None:
            gdf = gdf.to_crs(epsg)
        print("study area crs",str(gdf.crs))
        b = gdf.total_bounds   # [minx, miny, maxx, maxy]
        return list(map(float, b))
    