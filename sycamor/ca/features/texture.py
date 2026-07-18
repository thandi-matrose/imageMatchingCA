import rasterio
import math
import numpy as np
from skimage.feature import graycomatrix, graycoprops

PROPERTIES = ['energy','mean', 'entropy', 'variance']

def calculateGLCM(band, window_size=15):
    band = quantizing(band)
    texture = { prop: np.zeros((band.shape[0], band.shape[1])) for prop in PROPERTIES}
    
    for y in range(band.shape[0]):
        for x in range(band.shape[1]):
            window = band[y:y+window_size, x:x+window_size]
            
            glcm = graycomatrix(window, distances=[1], angles=[0, np.pi/4, np.pi/2, 3*np.pi/4], 
                                        levels=64, symmetric=True, normed=True)     
            for prop in PROPERTIES:
                val = graycoprops(glcm, prop)
                texture[prop][y, x] = np.mean(val)

    return texture
        
def getTextureBands(intensityData):
    return calculateGLCM(intensityData, window_size=15)

def quantizing(log_image, num_levels=64):
    # 1. Shift minimum to 0
    shifted = log_image - np.min(log_image)
    
    # 2. Normalize to [0, 1] range
    normalized = shifted / np.max(shifted)
    
    # 3. Quantize into discrete bins
    quantized = normalized * (num_levels - 1)
    
    # 4. Round and cast to integer (e.g., uint8 or uint16)
    return np.round(quantized).astype(np.uint8)


