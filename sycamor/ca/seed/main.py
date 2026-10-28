from datetime import datetime
import json
import os
from pprint import pp

from matplotlib import pyplot as plt
import numpy as np
from sycamor.ca.classification.scheme import LandClass, TrapezoidalDefinition
from pathlib import Path
import pandas as pd

from concurrent.futures import ProcessPoolExecutor
from sycamor.ca.features.localHeterogeneity import getSpeckleDivergence
from sycamor.ca.features.logIntensity import getLogIntensity
from sycamor.ca.features.parallelTexture import WINDOW_SIZE, TextureAnalyser
from sycamor.ca.features.set import Feature
import rasterio as rast

from sycamor.config.syCAMOR import SEEDING_CONFIDENCE_FILTER, WOODSTOCK_BOXES
from sycamor.retrieval.dataset import Dataset


new_dir = "/home/thandi/HONOURS/imageMatchingCA/" 
os.chdir(new_dir)
print(f"Changed directory to: {os.getcwd()}")


def getFeatures(raster,name):
    
    
    features = {}
        
    #Band 1
    band1 = raster.read(1)
    band2 = raster.read(2)
    
    features[Feature.LOG_INTENSITY] = getLogIntensity(band1)
    #Band 2
    features[Feature.SPECKLE_DIVERGENCE] = getSpeckleDivergence(features[Feature.LOG_INTENSITY])

    analyser = TextureAnalyser(features[Feature.LOG_INTENSITY])
    textureFeatures = analyser.calculateGLCM() 
    #Band 3
    features[Feature.ENERGY_GLCM] = textureFeatures["energy"]
    #Band 4
    features[Feature.MEAN_GLCM] = textureFeatures["mean"]
    #Band 5
    features[Feature.VARIANCE_GLCM] = textureFeatures["variance"]
    
    meta = raster.meta.copy()
    meta.update(count=5)
    
    with rast.open("data/geotiff/wood/"+name+".tif", "w", **meta) as dst:
        dst.write(features[Feature.LOG_INTENSITY], 1)  
        dst.write(features[Feature.SPECKLE_DIVERGENCE], 2) 
        dst.write(features[Feature.ENERGY_GLCM], 3) 
        dst.write(features[Feature.MEAN_GLCM], 4) 
        dst.write(features[Feature.VARIANCE_GLCM], 5) 
    
def openRaster(name):
    print("[READ] Opening raster " ,name)
    src =  rast.open(name)
    print("[DATA] Raster loaded. Raster info\n")
    print(src.meta)
    print("Spatial Resolution, X:",src.res[0])
    print("Spatial Resolution, Y:",src.res[1])
    width=src.width*src.res[0]
    height= src.height*src.res[1]
    print("Width: ", width, "m = ",width/1000," km")
    print("Height: ",height, "m = " ,height/1000,"km")
    print()
    
    return src    

def seedGridA(gridCell):
    
    dir_path = Path("results/records/sigOutputs/json/")
    
    mostRecent = datetime.min
    title = ""
    
    method = "narrow"
    
    for f in dir_path.glob("*"): 
        dateStr =  str(f)[-20:-5]
        dt_obj = datetime.strptime(dateStr, "%Y%m%d_%H%M%S")
        if (dt_obj > mostRecent):
            mostRecent = dt_obj
            title = f
    
    with open(title, 'r', encoding='utf-8') as file:
        data = json.load(file)
    
    featureList = list(Feature)
    band = 1
    name = gridCell
    dataset = Dataset()
    raster, record = dataset.getRaster(name)
    
    getFeatures(raster, name)
    
    raster = openRaster("data/geotiff/woodstock-salt/features/"+name+".tif")
    
    rows = raster.read(3).shape[0]
    columns = raster.read(3).shape[1]
    classRast = np.zeros((rows, columns))
    membershipRast =  np.zeros((len(list(LandClass))-1,rows, columns))
    
    weights = pd.read_csv("results/records/sigOutputs/feature_weights.csv")
    weights = weights[['feature', 'class_name', 'weight']]
    for i in range(rows):
        for j in range(columns):
            activeClass = 0
            highestProb = 0
            for landClass in list(LandClass):
                if landClass.displayName != "Undefined":
                    '''
                    minProb = 0
                    for feature in featureList:
                        
                        cellValue = raster.read(feature.index)[i][j]
                        trapezoid = TrapezoidalDefinition(**data["signatures"][landClass.displayName][feature.name], method=method )
                        prob = trapezoid.membership(cellValue)
                        
                        if (feature.index==1 or  (prob>0 and prob < minProb)):
                            minProb = prob
                    membershipRast[landClass.index-1][i][j] = minProb        
                    if minProb > highestProb:
                        activeClass = landClass.index
                        highestProb = minProb
                    '''
                    classWeight = list(weights.loc[(weights["class_name"] == landClass.displayName), "weight"])
                                        
                    probs = []
                    for feature in featureList:
                        
                        cellValue = raster.read(feature.index)[i][j]
                        trapezoid = TrapezoidalDefinition(**data["signatures"][landClass.displayName][feature.name], method=method )
                        prob = trapezoid.membership(cellValue)
                        probs.append(prob)

                    probs = np.multiply(classWeight,probs)
                    prob = np.sum(probs)
                    membershipRast[landClass.index-2][i][j] = prob
                    if prob > highestProb:
                        activeClass = landClass.index
                        highestProb = prob
                if highestProb > SEEDING_CONFIDENCE_FILTER:
                    classRast[i][j] = activeClass  
                
    meta = raster.meta.copy()
    meta.update(count=len(list(LandClass)))
    print(membershipRast[5])
    with rast.open("results/seed/"+name+".tif", "w", **meta) as dst:
        dst.write(classRast, 1)
        
        for landClass in list(LandClass):      
            if landClass.index !=0:
                dst.write(membershipRast[landClass.index-1], landClass.index+1)
_WORKER = {}

def _init_worker(bands, trapezoids, class_weights, class_indices,
                 feature_indices, n_classes, confidence):
    _WORKER.update(
        bands=bands, trapezoids=trapezoids, class_weights=class_weights,
        class_indices=class_indices, feature_indices=feature_indices,
        n_classes=n_classes, confidence=confidence,
    )

def _process_rows(row_range):
    rs, re = row_range
    w = _WORKER
    bands           = w['bands']            # (n_bands, H, W)
    trapezoids      = w['trapezoids']       # list[class] -> list[feature] of TrapezoidalDefinition
    class_weights   = w['class_weights']    # list[class] -> scalar or 1-D array
    class_indices   = w['class_indices']    # list[class] -> LandClass.index
    feature_indices = w['feature_indices']  # list[feature] -> band number (1-based)
    n_classes       = w['n_classes']
    confidence      = w['confidence']

    sub    = bands[:, rs:re, :]             # (n_bands, n_rows, n_cols)
    n_rows = re - rs
    n_cols = bands.shape[2]

    classRast      = np.zeros((n_rows, n_cols), dtype=np.float32)
    membershipRast = np.zeros((n_classes - 1, n_rows, n_cols), dtype=np.float32)

    n_feat = len(feature_indices)
    for i in range(n_rows):
        for j in range(n_cols):
            active = 0
            high   = 0.0
            for ci, class_index in enumerate(class_indices):
                
                probs = np.empty(n_feat, dtype=np.float32)
                for k, fidx in enumerate(feature_indices):
                    probs[k] = trapezoids[ci][k].membership(sub[fidx - 1, i, j])
                p = float(np.sum(class_weights[ci] * probs))
                membershipRast[class_index - 2, i, j] = p
                if p > high:
                    active = class_index
                    high   = p
                '''
                minProb = 2
                for k, fidx in enumerate(feature_indices):
                    prob = trapezoids[ci][k].membership(sub[fidx - 1, i, j])
                    if (prob >0 and minProb>prob):
                        minProb = prob
                if minProb == 2:
                    minProb = 0
                print
                membershipRast[class_index - 2, i, j] = minProb
                
                
                
                if minProb > high:
                    active = class_index
                    high   = minProb
               ''' 
            if high > confidence:
                classRast[i, j] = active

    return rs, re, classRast, membershipRast


def seedGrid(gridCell, n_workers=None):
    # ---------- pick latest signature JSON ----------
    dir_path = Path("results/records/sigOutputs/json/")
    mostRecent, title = datetime.min, ""
    for f in dir_path.glob("*"):
        dt_obj = datetime.strptime(str(f)[-20:-5], "%Y%m%d_%H%M%S")
        if dt_obj > mostRecent:
            mostRecent, title = dt_obj, f
            
    print(title)
    with open(title, 'r', encoding='utf-8') as file:
        data = json.load(file)

    method      = "narrow"
    featureList = list(Feature)

    # ---------- fetch / build feature stack ----------
    name = gridCell
    dataset = Dataset()
    raster, _ = dataset.getRaster(gridCell)
    getFeatures(raster, name)
    raster = openRaster("data/geotiff/wood/" + name + ".tif")

    rows, columns = raster.height, raster.width

    # Read every band exactly once.
    max_band = max(f.index for f in featureList)
    bands = np.empty((max_band, rows, columns), dtype=np.float32)
    for f in featureList:
        bands[f.index - 1] = raster.read(f.index)

    # ---------- pre-compute everything that doesn't depend on the cell ----------
    class_list = [lc for lc in LandClass if lc.displayName != "Undefined"]

    trapezoids = [
        [TrapezoidalDefinition(**data["signatures"][lc.displayName][f.name], method=method)
         for f in featureList]
        for lc in class_list
    ]

    weights = pd.read_csv("results/records/sigOutputs/feature_weights.csv")
    weights = weights[['feature', 'class_name', 'weight']]
    class_weights = []
    for lc in class_list:
        w = list(weights.loc[weights["class_name"] == lc.displayName, "weight"])
        class_weights.append(np.asarray(w[0] if len(w) == 1 else w, dtype=np.float32))

    class_indices   = [lc.index for lc in class_list]
    feature_indices = [f.index for f in featureList]
    n_classes       = len(list(LandClass))

    # ---------- parallelise over row chunks ----------
    n_workers = n_workers or os.cpu_count()
    n_chunks  = n_workers * 4                                  # for load balancing
    edges = np.linspace(0, rows, n_chunks + 1, dtype=int)
    row_ranges = [(int(edges[k]), int(edges[k + 1]))
                  for k in range(n_chunks) if edges[k] < edges[k + 1]]

    classRast      = np.zeros((rows, columns), dtype=np.float32)
    membershipRast = np.zeros((n_classes - 1, rows, columns), dtype=np.float32)

    with ProcessPoolExecutor(
        max_workers=n_workers,
        initializer=_init_worker,
        initargs=(bands, trapezoids, class_weights,
                  class_indices, feature_indices, n_classes,
                  SEEDING_CONFIDENCE_FILTER),
    ) as ex:
        for rs, re, cr, mr in ex.map(_process_rows, row_ranges):
            classRast[rs:re]      = cr
            membershipRast[:, rs:re, :] = mr

    # ---------- write output ----------
    meta = raster.meta.copy()
    meta.update(count=n_classes,  dtype="float32")
    with rast.open("results/seed/" + name + ".tif", "w", **meta) as dst:
        dst.write(classRast, 1)
        for lc in LandClass:
            if lc.index != 0:
                dst.write(membershipRast[lc.index - 1].astype("float32"), lc.index + 1)  
if __name__ == "__main__" :
    seedGrid("W08A_1") 
    
                        