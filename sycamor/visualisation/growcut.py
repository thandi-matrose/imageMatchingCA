

from datetime import datetime

from matplotlib import colors, pyplot as plt
import rasterio

from sycamor.ca.classification.scheme import LandClass
from sycamor.config.syCAMOR import WOODSTOCK_BOXES
from sycamor.visualisation.plot import addStyle


def plotAllGrowCut():
    fig, axes = plt.subplots(nrows=4, ncols=4, figsize=(15,10),layout="compressed")
    #plt.tight_layout(pad=0, h_pad=0, w_pad=0)

    levels = [] 
    for value in LandClass.getValues():
        levels.append(value-0.5)
        
    levels.append(8.5)    
    colours =LandClass.getColours()


    cmap, norm = colors.from_levels_and_colors(levels, colours)
    axes = axes.flat
    for i in range(len(WOODSTOCK_BOXES)):
        ax = axes[i]
        ax.set_xticks([]) 
        ax.set_yticks([]) 
        
        cell = WOODSTOCK_BOXES[i]
        with rasterio.open(f"results/growcut/otherwoodstock/{cell}.tif") as src:
            band=src.read(1)
        im = ax.imshow(band, cmap=cmap, norm=norm, interpolation='nearest')
        ax.text(10,20, cell,zorder=5)
   
    '''
    cbar = plt.colorbar(im, ax=plt.gca(), ticks=class_ticks)
    cbar.set_ticklabels(class_labels)
    cbar.set_label('Class', fontsize=12)
    '''
    plt.savefig("results/growcut/allgc"+"_"+datetime.now().strftime("%Y%m%d_%H%M%S")+".png", dpi=300, bbox_inches='tight')
    
    ax.clear() 
    
        
if __name__ == "__main__":
    addStyle()
    plotAllGrowCut()
    
