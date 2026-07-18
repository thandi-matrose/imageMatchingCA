import numpy as np
from skimage.feature import graycomatrix, graycoprops
from joblib import Parallel, delayed

from sycamor.ca.features.logIntensity import getLogIntensity
from sycamor.ca.set import LOG_INTENSITY
from sycamor.retrieval import dataset
from sycamor.visualisation.plot import plotHistogram, plotRadar

window_size = 15
properties = ['energy','mean', 'entropy', 'variance']

num_levels=64

def calculate_glcm_features(patch):
    """Calculates GLCM features for a single image patch."""
    
    # Compute GLCM
    glcm = graycomatrix(
        patch, 
        distances=[1], 
        angles=[0, np.pi/4, np.pi/2, 3*np.pi/4], 
        levels=256, 
        symmetric=True, 
        normed=True
    )
    texture = {}
    # Extract texture properties
    for prop in properties:
        val = graycoprops(glcm, prop)
        texture[prop] = np.mean(val)
        
    return texture
    
    
def batchCalc(band):
    texture = { prop: np.zeros((band.shape[0], band.shape[1])) for prop in properties}
    
    band = quantizing(band)
    # Assume 'patches' is a list of cropped image segments
    # Use n_jobs=-1 to use all available CPU cores
    
    patches = []
    results = []
    for y in range(band.shape[0]):
        results.append([])
        
        rowPatches = []
        for x in range(band.shape[1]):
            rowPatches.append(band[y:y+window_size, x:x+window_size])  
       
        results[y] = Parallel(n_jobs=-1)(
            delayed(calculate_glcm_features)(patch) for patch in rowPatches
        )

    features_array =results
    
    print(features_array)
    
    return features_array

def quantizing(log_image):
    # 1. Shift minimum to 0
    shifted = log_image - np.min(log_image)
    
    # 2. Normalize to [0, 1] range
    normalized = shifted / np.max(shifted)
    
    # 3. Quantize into discrete bins
    quantized = normalized * (num_levels - 1)
    
    # 4. Round and cast to integer (e.g., uint8 or uint16)
    return np.round(quantized).astype(np.uint8)


def main():
    DATASET = dataset.Dataset()
    raster, record = DATASET.getRandomRaster()
    plotRadar(raster, record)
    features = {}
    
    #Band 1
    band1 = raster.read(1)
    band2 = raster.read(2)
   
    features[LOG_INTENSITY] = (getLogIntensity(band1), getLogIntensity(band2))
    
    textureFeatures = batchCalc(features[LOG_INTENSITY][0])
    
    plotHistogram(textureFeatures)

main()