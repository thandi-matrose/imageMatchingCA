""" Tests for the growcut module """

import csv
from datetime import datetime
import os

import rasterio as rast

import numpy as np
import matplotlib.pyplot as plt
import sys
import nibabel as nib
import time
from scipy.ndimage.morphology import binary_dilation, binary_erosion

from sycamor.ca.classification.scheme import LandClass
from sycamor.config.syCAMOR import SAMPLE_BOXES, WOODSTOCK_BOXES
from sycamor.retrieval.dataset import Dataset
from sycamor.visualisation.plot import addStyle
from sycamor.visualisation.seedPlotter import plotClassified, plotSeed


new_dir = "/home/thandi/HONOURS/imageMatchingCA/" 
os.chdir(new_dir)
print(f"Changed directory to: {os.getcwd()}")
from evaluation.growcut.modules.growcut_cpu import fastgc

def segment(gridCell):
    
    dataset = Dataset()
    radarRaster, record = dataset.getRaster(gridCell)
    TRAINING_PATH = "sycamor/ca/classification/merged/"
    SEED_PATH = "results/seed/"
    RADAR_PATH = "data/radar/hart94/"
    filename = "W08A_1_HART94_20260713_110308.tiff"
    GROWCUT_PATH = "results/growcut/"
    outSegmentName = "results/growcut/"+gridCell+"_segmented.png"
    outLabelName ="results/growcut/"+gridCell+"_label.png"
    radarFileName = record.Hart94Filename
    img = radarRaster.read(1)
    seedFileName = SEED_PATH+gridCell+".tif"
    with rast.open(seedFileName) as labels:
        seeds = labels.read(1)
        
        start_time = time.perf_counter()
        segmented = fastgc(np.array(img).astype(int),seeds)
        end_time = time.perf_counter()

        elapsed_time = end_time - start_time
        
        with open(GROWCUT_PATH+"data.csv", "a", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            #columns = [["timestamp", "grid_cell","class", "processing_time", "n_seeds", "output_file", "output_labels", "radar_file" ,"seed_file"]]
            
            data = []
            values, counts = np.unique(seeds, return_counts=True)
            
            for val, cnt in zip(values, counts):
                if val!=0: data.append([str(datetime.now()), gridCell, LandClass.from_index(val).displayName, elapsed_time, cnt, outSegmentName, outLabelName, radarFileName, seedFileName ])
            writer.writerows(data)
            
        plotClassified(segmented[1], outLabelName)
        outdir = "results/growcut/woodstock/"
        
        meta = labels.meta.copy()
        meta.update(count=2)
        
        with rast.open(outdir+gridCell+".tif", "w", **meta) as dst:
            dst.write(segmented[1], 1)
            dst.write(segmented[0], 1)

def plotGrowCut():
    for box in WOODSTOCK_BOXES:
        path = f'results/growcut/{box}.tif'
        with rast.open(path) as src:
            img = src.read(2)
        plotClassified(img, f"results/growcut/woodstock/{box}_gc.png", False)
   
def otherMain():
    addStyle()
    #CELLS = ["W58A_15","W08A_1", "W44D_8"]
    for cell in WOODSTOCK_BOXES:
        segment(cell)

if __name__ == "__main__":
    otherMain() 
