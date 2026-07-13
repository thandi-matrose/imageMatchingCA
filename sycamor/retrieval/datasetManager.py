import os
from typing import Optional
import numpy as np
import rasterio as rasterio
import rasterio.warp
import fiona
import time
from datetime import datetime

import geopandas as gpd

from sycamor.retrieval import utils

WOODSTOCK = "sycamor/retrieval/studyarea/Official_Planning_Suburbs.shp"

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
    
    def writeImage(self, data, file):
        with open('data/radar/'+file+datetime.now().strftime("%Y%m%d_%H%M%S")+".tiff", 'wb') as file:
            file.write(data)
            
def getBounds( path, epsg = utils.EPSG): 
    
    with rasterio.open("data/"+path) as src:
        data = src.read()
        
        # View file metadata
        print(f"Bands: {src.count}, Height: {src.height}, Width: {src.width}")
        print(f"Coordinate Reference System (CRS): {src.crs}")   
        
         
        print("study area crs",str(src.crs))
        
        objbounds = rasterio.warp.transform_bounds(src_crs=src.crs, dst_crs=rasterio.CRS.from_epsg(epsg), left=src.bounds.left, bottom=src.bounds.bottom, right=src.bounds.right, top=src.bounds.top)

        bounds = list(map(float, objbounds))
        print(bounds)
        return bounds

   
class StudyArea:
    def __init__(self, pathToFile: Optional[str] = WOODSTOCK):
            # Reading the shapefile into a GeoDataFrame
            self.studyArea = gpd.read_file(pathToFile)
           
            
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
        bounds = list(map(float, b))
        print(bounds)
        return bounds
    