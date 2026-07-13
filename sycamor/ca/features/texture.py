import rasterio
import math
import numpy as np
from skimage.feature import graycomatrix, graycoprops
from skimage.util import view_as_windows
import matplotlib.pyplot as plt



def calculateGLCM(band, window_size=15):
    properties = ['energy','mean', 'entropy', 'variance']
   
    band = quantizing(band)
    
    texture = { prop: np.zeros((band.shape[0], band.shape[1])) for prop in properties}
    
    for y in range(band.shape[0]):
        for x in range(band.shape[1]):
            window = band[y:y+window_size, x:x+window_size]
            
            glcm = graycomatrix(window, distances=[1], angles=[0], 
                                        levels=64, symmetric=True, normed=True)
            
            for prop in properties:
                val = graycoprops(glcm, prop)
                texture[prop][y, x] = np.mean(val)

    
    return texture

def plotTextures(images=[]) :
    if (len(images)>1):
        rows, columns = factorsOfLeastDifference(len(images))

        fig, axes = plt.subplots(rows, columns, figsize=(10, 5))
        
        count = 0
        
        nextImg = images[count]

        for i in range(rows):
            for j in range(columns):
                # Plot the first matrix
                im1 = axes[i,j].imshow(nextImg, cmap='viridis', interpolation='nearest')
                axes[i,j].set_title(f'Matrix {i} (Random Data)')
                axes[i,j].axis('off')  # Optional: hide axes ticks
                fig.colorbar(im1, ax=axes[i,j], fraction=0.046, pad=0.04)
                count+=1
                if count < len(images):
                    nextImg = images[0]
    else:
        plt.imshow(images[0], cmap='viridis', interpolation='nearest')
        plt.colorbar(fraction=0.046, pad=0.04)
    # Add labels and display
    plt.title("Matrix as a Colour Image")
    plt.xlabel("Columns")
    plt.ylabel("Rows")
    

    plt.tight_layout()
    plt.show()
    
    
def factorsOfLeastDifference(n):
   
    for i in range(int(math.isqrt(n)), 0, -1):
        if n % i == 0:
            factor1 = i
            factor2 = n // i
            return factor1, factor2
        
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