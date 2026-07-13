from datetime import datetime

import geopandas as gpd
import os
import rasterio as rast
from scipy import stats
from sycamor.retrieval.main import getRadarDataset
from rasterio.warp import calculate_default_transform, reproject, Resampling
import numpy as np
import pprint as pp

new_dir = "/home/thandi/HONOURS/imageMatchingCA/" 
os.chdir(new_dir)
print(f"Changed directory to: {os.getcwd()}")




class Dataset:
    
    radarDataframe = []
    HART94 = ""
    
    def __init__(self):
        vectorGdf =  gpd.read_file("data/shp/2024_Aerial_Imagery_1kmx1km_Grid.shp")
        result = vectorGdf.merge(getRadarDataset(), on='GRID_CELL', how='left')
        self.radarDataframe = result
        
        with rast.open("data/geotiff/woodstock-salt/1km_RGB_5cm_W45A_21_0.TIF") as ref:
            self.HART94 = ref.crs
        
    
    def convertToHart94(self, src, name):
        
        dst_crs = self.HART94
        
        transform, width, height = calculate_default_transform(
            src.crs, 
            dst_crs, 
            src.width, 
            src.height, 
            *src.bounds
        )
        
        kwargs = src.profile.copy()
        kwargs.update({
            'crs': dst_crs,
            'transform': transform,
            'width': width,
            'height': height
        })
        newName = "data/radar/hart94/"+name+"_HART94_"+datetime.now().strftime("%Y%m%d_%H%M%S")+".tiff"
        with rast.open(newName, "w", **kwargs) as dst:
            for i in range(1, src.count + 1):
                reproject(
                    source=rast.band(src, i),
                    destination=rast.band(dst, i),
                    src_transform=src.transform,
                    src_crs=src.crs,
                    dst_transform=transform,
                    dst_crs=dst_crs,
                    resampling=Resampling.nearest # Use Resampling.bilinear for continuous data
                )
        return rast.open(newName)        
                
    def getRandomRaster(self):
        randomRecord = self.radarDataframe.sample(n=1)
        print("\n\nRandomly selected record:")
        print(randomRecord)
        name = "data/radar/hart94/" + randomRecord["Hart94Filename"].values[0]
        print("[READ] Opening raster " , name)
        src =  rast.open(name)
        print("[DATA] Raster loaded. Raster info\n")
        pp.pprint(src.meta)
        print("Spatial Resolution, X:",src.res[0])
        print("Spatial Resolution, Y:",src.res[1])
        width=src.width*src.res[0]
        height= src.height*src.res[1]
        print("Width: ", width, "m = ",width/1000," km")
        print("Height: ",height, "m = " ,height/1000,"km")
        print()
        
        return src,randomRecord


