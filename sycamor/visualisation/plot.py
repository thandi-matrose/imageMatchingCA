from datetime import datetime
from pprint import pprint
import rasterio as rast
import numpy as np
from matplotlib import pyplot as plt
from rasterio.plot import show, adjust_band, show_hist
from sycamor.ca.features.localHeterogeneity import getSpeckleDivergence
from sycamor.ca.features.logIntensity import getLogIntensity
from sycamor.ca.features.set import Feature
from sycamor.retrieval import dataset 

from matplotlib import font_manager


def plotRGBImage(src, title="Image"): 
    addStyle()
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
    
def distributionFeature(band1, feat:Feature, record ):
    addStyle()
    band1 = band1.flatten()
    title = ""
    title = record["GRID_CELL"].values[0]
    print(title)
    plotHistoPlot(band1,"Distribution of " + feat.nameStr + " of " + title, unit=feat.nameStr )
    #plotBoxplot(band1, "Boxplot of " + feat.nameStr + " of " + title)
    #plotHistogram(band1, "Histogram of " + feat.nameStr + " of " + title)
    
def plotHistoPlot(band1, title="", unit=""):
    
    addStyle()
    band1= band1.flatten()
    
    
    
    print("[PLOT] Plotting " + title + "...")
        # 2. Create subplots sharing the x-axis
    fig, (ax_hist, ax_box) = plt.subplots(2, 1, sharex=True, gridspec_kw={"height_ratios": (0.75, 0.25)})
    
    # 3. Plot the horizontal boxplot on the top axis (ax_box)
    ax_box.boxplot(band1, vert=False, patch_artist=True, boxprops=dict(facecolor="#7ca86d", edgecolor='black'), medianprops=dict(color='black', linewidth=2))
    ax_box.yaxis.set_visible(False)
    ax_box.xaxis.tick_top()
    ax_box.xaxis.set_label_position('top')

    # 4. Plot the histogram on the bottom axis (ax_hist)
    counts, bins, patches = ax_hist.hist(band1, bins="auto", color="#7ca86d", edgecolor='black')
    ax_hist.set_xlabel(unit)
    ax_hist.set_ylabel('Frequency')
    ax_hist.xaxis.set_tick_params(labelbottom=True)
    
    

    # 5. Clean up layout and display
    plt.tight_layout()
    plt.subplots_adjust(top=0.92) 
    fig.suptitle(title)
    plt.savefig('results/featureSet/histoplot/'+title+"_"+str(datetime.now().strftime("%Y%m%d_%H%M%S"))+'.png', dpi=300, bbox_inches='tight')
    plt.show()
    print("[WRITE] " + title + " written to results/radar/featureSet/boxplot/...")
        

def plotBoxplot(band1, title=""):
    addStyle()
    plt.boxplot(band1.flatten()) 
    print("[PLOT] Plotting " + title + "...")

    plt.ylabel("Intensity (dB)")
    plt.xlabel(" ")
    plt.title(title)
   
    plt.savefig('results/featureSet/boxplot/'+title+"_"+str(datetime.now().strftime("%Y%m%d_%H%M%S"))+'.png', dpi=300, bbox_inches='tight')
    plt.show()
    print("[WRITE] " + title + " written to results/radar/featureSet/boxplot/...")
    
def plotHistogram(src, title="", bins=15):
    addStyle()
    print("[PLOT] Plotting " + title + "...")
    data = src.flatten()
    print(data) 
    plt.hist(
        data, 
        bins=50
    )
    
    plt.xlabel("Intensity (dB)")
    plt.ylabel("Frequency (Number of pixels)")
    plt.title(title)
   
    plt.savefig('results/featureSet/histogram/'+title+"_"+str(datetime.now().strftime("%Y%m%d_%H%M%S"))+'.png', dpi=300, bbox_inches='tight')
    plt.show()
    print("[WRITE] " + title + " written to results/featureSet/histogram/...")
    
          
def plotRadar(dataset, record):   
    addStyle()
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
    plt.savefig('results/radar/'+record.GRID_CELL.values[0]+"_"+str(datetime.now().strftime("%Y%m%d_%H%M%S"))+'.png', dpi=300, bbox_inches='tight')
    plt.show()

def plotFeatureSet(features, rasterName =""):
    addStyle()
    for i in range(2):
        fig, axes = plt.subplots(2, 3, figsize=(18, 9))
        
        band1 = features[Feature.LOG_INTENSITY][i]
        band2 = features[Feature.SPECKLE_DIVERGENCE][i]
        band3 = features[Feature.ENERGY_GLCM][i]
        band4 = features[Feature.MEAN_GLCM][i]
        band5 = features[Feature.VARIANCE_GLCM][i]
        
        subtitle = (
            "Feature Set"
        )

        img1 = plt.imread('figures/FeatureSet.png')
        axes[0,0].text(0, 0.5, rasterName.values[0], 
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
        plt.savefig('results/featureSet/'+datetime.now().strftime("%Y%m%d_%H%M%S")+"_"+rasterName.values[0]+'.png', dpi=300, bbox_inches='tight')
        plt.show()

def addStyle():
    font_path = "/usr/share/texmf/fonts/opentype/public/lm-math/latinmodern-math.otf"
    font_manager.fontManager.addfont(font_path)
    plt.rcParams['font.family'] = 'serif'
    plt.rcParams['font.serif'] = ['Latin Modern Math']
    plt.rcParams['font.size'] = 10
    
def main():
    
        addStyle()
        data = dataset.Dataset()
        raster, record = data.getRandomRaster()
        plotRadar(raster, record)
        
        features = {}
        
        #Band 1
        band1 = raster.read(1)
        band2 = raster.read(2)
       
        features[Feature.LOG_INTENSITY] = (getLogIntensity(band1), getLogIntensity(band2))
        
        
        distributionFeature(features[Feature.LOG_INTENSITY][0], Feature.LOG_INTENSITY, record)
        #Band 2
        features[Feature.SPECKLE_DIVERGENCE] = (getSpeckleDivergence(features[Feature.LOG_INTENSITY][0]), getSpeckleDivergence(features[Feature.LOG_INTENSITY][1]))
           
        
def test():
        # 1. Generate sample data
    addStyle()
    data = dataset.Dataset()
    
    plotGrid(data, "W45A_12")
    #plotGrid(data, "W17D_14")
def plotGrid(data, name):
    record = data.radarDataframe[data.radarDataframe['GRID_CELL'] == name]
    print(record)
    filename = record['Hart94Filename'].values[0]
    raster =  data.openRaster(filename)
    distributionFeature(getLogIntensity(raster.read(2)), Feature.LOG_INTENSITY, record) 
if __name__ == "__main__":
    test()