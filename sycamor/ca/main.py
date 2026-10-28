#MAIN WORKFLOW
import csv
import time

import rasterio

from sycamor.ca.classification.merged.ClassifiedDataset import getTrainingFeatureSet
from sycamor.ca.classification.summariser import summariseTrainingSet
from sycamor.ca.features.main import getFeatureSet
from sycamor.ca.region_growing.main import growing
from sycamor.ca.seed.main import seedGrid
from sycamor.config.syCAMOR import SAMPLE_BOXES, WOODSTOCK_BOXES
from sycamor.visualisation.seedData import plotMembership, plotTrainingSet
from sycamor.visualisation.seedPlotter import plotClassified, plotSeed

def getTraining():
    getTrainingFeatureSet(SAMPLE_BOXES)
    
    
    
def classify():
    #plotTrainingSet()
    box = ["W45C_6"]
    data = []
    for grid in WOODSTOCK_BOXES:
       
        start_time = time.perf_counter()
        seedGrid(grid)
        end_time = time.perf_counter()
        elapsed_time = end_time - start_time
        data.append([grid, elapsed_time])
        elapsed_time = end_time - start_time
        #plotMembership(grid)
        #plotSeed(grid)
        writeElapseSeed(data)
        '''
        data = []
        start_time = time.perf_counter()
        seedlayers = growing(grid)
        
        end_time = time.perf_counter()
        elapsed_time = end_time - start_time
        data.append([grid, elapsed_time])
        writeElapseGrowing(data)
        
        '''  
def writeElapseSeed(data):
    with open("results/seed/time.csv", "a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerows(data)
def writeElapseGrowing(data):
    with open("results/seed/growing.csv", "a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerows(data)
        
def plotGrown():
    for box in ["W45C_6"]:
        path = f'results/growing/tweaked/{box}.tif'
        with rasterio.open(path) as src:
            img = src.read(1)
        plotClassified(img, f"results/growing/tweaked/{box}.png", False)
    
def main():
    #getTraining()
    #summariseTrainingSet()
    #plotMembership("W45C_6")
    classify()
    plotGrown()
    
    

if __name__ == "__main__":
    main()