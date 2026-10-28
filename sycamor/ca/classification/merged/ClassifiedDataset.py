import csv
from datetime import datetime

import numpy as np
import rasterio

import os
from sycamor.ca.features.main import getFeatureSet
from sycamor.ca.features.parallelTexture import WINDOW_SIZE
from sycamor.ca.features.set import Feature
from sycamor.config.syCAMOR import SAMPLE_BOXES
from sycamor.retrieval.dataset import Dataset


new_dir = "/home/thandi/HONOURS/imageMatchingCA/" 
os.chdir(new_dir)
print(f"Changed directory to: {os.getcwd()}")

CSV_DIR_PATH = "results/records/run2/data.csv"
MERGED_DIR_PATH = "data/merged/"

POLARISATIONS = ["VV", "VH"]

            
def getTrainingFeatureSet(SAMPLE_BOXES):
    with open(CSV_DIR_PATH, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["date", "polarisation", "GRID CELL", "row", "column", "class", "log_intensity", "speck_diverge", "glcm_energy", "glcm_mean", "glcm_variance", "x", "y" ])
        
    for cell in SAMPLE_BOXES:  
        with rasterio.open(MERGED_DIR_PATH+"merge_"+cell+".tif") as src:
            vV = src.read(1)
            vH = src.read(2)
            classified = src.read(3)
            sourceMeta = src
        print(cell)
        DATASET = Dataset()
        features = getFeatureSet(DATASET,cell)
        meta = sourceMeta.meta.copy()
        meta.update(count=5)
        
        with rasterio.open("data/geotiff/wood/"+cell+".tif", "w", **meta) as dst:
            dst.write(features[Feature.LOG_INTENSITY][0], 1)  
            dst.write(features[Feature.SPECKLE_DIVERGENCE][0], 2) 
            dst.write(features[Feature.ENERGY_GLCM][0], 3) 
            dst.write(features[Feature.MEAN_GLCM][0], 4) 
            dst.write(features[Feature.VARIANCE_GLCM][0], 5) 
        with open(CSV_DIR_PATH, 'a', newline='') as f:
            writer = csv.writer(f)
            #writer.writerow(["data", "polarisation", "GRID CELL", "row", "column", "class", "log_intensity", "speck_diverge", "glcm_energy", "glcm_mean", "glcm_variance", "x", "y" ])
            # Iterate through every pixel row and column
            for i in range(vH.shape[0]-WINDOW_SIZE):
                for j in range(vV.shape[1]-WINDOW_SIZE):
                    # Calculate spatial coordinates from row, col
                    
                    if (classified[i, j] != 0 and classified[i, j] != None):
                        x, y = sourceMeta.xy(i, j)
                        
                
                        for pol in range(len(POLARISATIONS)):
                            data = []
                            
                            #Col1: Date 
                            data.append(""+str(datetime.now()))
                            #Col2: Polaris 
                            data.append(POLARISATIONS[pol])
                            
                            #Col3: Grid Cell 
                            data.append(cell)
                            
                            #Col4: row 
                            data.append(i)
                            
                            #Col3: col 
                            data.append(j)
                            
                            #Col class
                            data.append(classified[i, j])
                            
                            #Col
                            data.append(features[Feature.LOG_INTENSITY][pol][i][j])
                            
                            data.append(features[Feature.SPECKLE_DIVERGENCE][pol][i][j])
                            
                            data.append(features[Feature.ENERGY_GLCM][pol][i][j])
                            
                            data.append(features[Feature.MEAN_GLCM][pol][i][j])
                            
                            data.append(features[Feature.VARIANCE_GLCM][pol][i][j])
            
                            data.append(x)
                            
                            data.append(y)
                            
                            writer.writerow(data)


if __name__ == "__main__":
    getTrainingFeatureSet(SAMPLE_BOXES)