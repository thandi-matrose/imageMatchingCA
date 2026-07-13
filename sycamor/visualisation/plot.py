from datetime import datetime
from pprint import pprint

import rasterio as rast
import numpy as np
from matplotlib import pyplot as plt
from rasterio.plot import show, adjust_band, show_hist

from sycamor.ca.set import ENERGY_GLCM, LOG_INTENSITY, MEAN_GLCM, SPECKLE_DIVERGENCE, VARIANCE_GLCM
def plotRGBImage(src, title="Image"): 
    band1 = src.read(1)
    print("Dataset Transform:")
    print(src.transform)
    height = band1.shape[0]
    width = band1.shape[1]
    cols, rows = np.meshgrid(np.arange(width), np.arange(height))
    
    xs, ys = rast.transform.xy(src.transform, rows, cols)
    print(xs)
    print(ys)
    xsRawDiff = np.diff(xs)
    mask = np.ones(xsRawDiff.size, dtype=bool)

    # Set the elements at every nth index (starting from index n-1) to False
    mask[width-1::width] = False 
    xsDiff = xsRawDiff[mask]
    # Apply the mask to 
    pixelRes = np.average(xsDiff)

    print(pixelRes, "m")

    ys_2d = (ys.reshape(width, height).T).flatten()

    ysRawDiff = np.diff(ys_2d)
    mask = np.ones(ysRawDiff.size, dtype=bool)

    # Set the elements at every nth index (starting from index n-1) to False
    mask[height-1::height] = False 
    ysDiff = ysRawDiff[mask]
    # Apply the mask to 
    pixelRes = np.average(ysDiff)

    print(pixelRes, "m")


    cols, rows = np.meshgrid(np.arange(width), np.arange(height))
    x, y = src.transform * (rows, cols)

    imgdata = np.array([adjust_band(src.read(i)) for i in (3,2,1)])
    plt.title(title)
    show(imgdata)
    
def distributionLogIntensity(band1, record):
    band1 = band1.flatten()
    plotBoxplot(band1, "Histogram of Log Intensity of " + record.Hart94Filename.values[0])
    plotHistogram(band1, "Histogram of Log Intensity of " + record.Hart94Filename.values[0])

def plotBoxplot(band1, title=""):
    plt.boxplot(band1.flatten()) 
    print("fLATTEN")
    pprint(band1.flatten())
    plt.ylabel("Intensity (dB)")
    plt.title(title)
    plt.show()
    
def plotHistogram(src, title="Histogram", bins=15):
    data = src.flatten()
    print(data) 
    plt.hist(
        data, 
        bins=50
    )
    plt.ylabel("Frequency (Number of pixels)")
    plt.title(title)
    plt.show()
    
          
def plotRadar(dataset, record):   
    
    band1 = dataset.read(1)
    band2 = dataset.read(2)

    fig, (ax1, ax2, ax3, ax4) = plt.subplots(1, 4, figsize=(12, 6))
    

    im1 = ax1.imshow(band1, cmap='viridis')
    ax1.set_title('Polarisation VV')
    
    ax1.axis('off') 

    im2 = ax2.imshow(band2, cmap='viridis')
    ax2.set_title('Polarisation VH')
    ax2.axis('off')
    
    im3 = ax3.imshow(band1 - band2, cmap='magma')
    ax3.set_title('Difference VV-VH')
    ax3.axis('off') 
    
    im4 = ax4.imshow(band1 / band2, cmap='Greens')
    ax4.set_title('Ratio VV/VH')
    ax4.axis('off') 

    fig.colorbar(im1, ax=ax1, shrink=0.7)
    fig.colorbar(im2, ax=ax2, shrink=0.7)
    fig.colorbar(im3, ax=ax3, shrink=0.7)
    fig.colorbar(im4, ax=ax4, shrink=0.7)
    
    fig.suptitle(record.Hart94Filename.values[0].split(".")[0], fontsize=16, fontweight="bold")

    plt.tight_layout()
    plt.savefig('results/radar/'+record.Hart94Filename.values[0]+"_"+datetime.now().strftime("%Y%m%d_%H%M%S")+'.png', dpi=300, bbox_inches='tight')
    plt.show()

def plotFeatureSet(features, rasterName =""):
    
    for i in range(2):
        fig, axes = plt.subplots(2, 3, figsize=(18, 9))
        
        band1 = features[LOG_INTENSITY][i]
        band2 = features[SPECKLE_DIVERGENCE][i]
        band3 = features[ENERGY_GLCM][i]
        band4 = features[MEAN_GLCM][i]
        band5 = features[VARIANCE_GLCM][i]
        
        subtitle = (
            "Feature Set"
        )

        
        img1 = plt.imread('figures/FeatureSet.png')
        axes[0,0].text(0, 0.5, rasterName, 
                transform=axes[0,0].transAxes, 
                fontsize=18, 
                va='top', 
                ha='left', 
                wrap=True)
        axes[0,0].text(0, 0, subtitle, 
                transform=axes[0,0].transAxes, 
                fontsize=15, 
                va='top', 
                ha='left', 
                wrap=True)
        axes[0,0].imshow(img1)
        axes[0,0].axis('off')

        im1 = axes[0,1].imshow(band1, cmap='YlOrRd')
        axes[0,1].set_title('Band 1: Logarithmic Intensity')
        
        im2 = axes[0,2].imshow(band2, cmap='magma')
        axes[0,2].set_title('Band 2: Speckle Divergence')
        
        im3 = axes[1,0].imshow(band3, cmap='YlGn')
        axes[1,0].set_title('Band 3: Energy GLCM')
        
        im4 = axes[1,1].imshow(band4, cmap='viridis')
        axes[1,1].set_title('Band 4: Mean GLCM')
        
        im5 = axes[1,2].imshow(band5, cmap='Greens')
        axes[1,2].set_title('Band 5: Variance GLCM')
        
        fig.colorbar(im1, ax=axes[0,1], shrink=0.7)
        fig.colorbar(im2, ax=axes[0,2], shrink=0.7)
        fig.colorbar(im3, ax=axes[1,0], shrink=0.7)
        fig.colorbar(im4, ax=axes[1,1], shrink=0.7)
        fig.colorbar(im5, ax=axes[1,2], shrink=0.7)
        
        
        plt.tight_layout()
        plt.savefig('results/featureSet/'+datetime.now().strftime("%Y%m%d_%H%M%S")+'.png', dpi=300, bbox_inches='tight')
        plt.show()


def main():
    features = []
    for i in range(6):
        rng = np.random.default_rng()
        matrix = rng.random((256, 256))
        features.append(matrix)
    plotFeatureHistogram(features)
    
if __name__ == "__main__":
    main()