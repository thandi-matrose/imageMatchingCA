
from matplotlib import pyplot as plt
import rasterio
from sycamor.ca.features.set import Feature
from sycamor.config.syCAMOR import WOODSTOCK_BOXES
from sycamor.retrieval.dataset import Dataset
from sycamor.visualisation.plot import addStyle

from pathlib import Path
import rasterio
from rasterio.merge import merge
import rasterio
from rasterio.merge import merge
from contextlib import ExitStack

def mosaic():
    output_path = "data/geotiff/wood/mosaic_multiband.tif"
    paths = [f"data/geotiff/wood/{p}.tif" for p in WOODSTOCK_BOXES]

    with ExitStack() as stack:
        # open all inputs, auto-close on exit
        sources = [stack.enter_context(rasterio.open(p)) for p in paths]

        # Merge ALL bands in one shot -> array shape (count, H, W)
        mosaic_arr, out_transform = merge(sources)

        meta = sources[0].meta.copy()
        meta.update(
            height=mosaic_arr.shape[1],
            width=mosaic_arr.shape[2],
            transform=out_transform,
            count=mosaic_arr.shape[0],
        )

        with rasterio.open(output_path, "w", **meta) as dst:
            # A single write of the 3-D array – no shape/index ambiguity
            dst.write(mosaic_arr)
def plotFeatures(gridCell):
    features = []
    with rasterio.open(f"data/geotiff/wood/{gridCell}.tif", "r") as src:
        for f in list(Feature):
            features.append(src.read(f.index))
    for f in list(Feature):        
        plt.imshow(features[f.index-1], cmap=f.colourMap) 
        plt.axis('off')
        plt.savefig(f"data/geotiff/wood/{gridCell}_{f}.png", dpi=150, bbox_inches="tight", pad_inches=0)  
        
        plt.clf()
def plotRadar(raster, gridCell):
    
    plt.imshow(raster, cmap="twilight") 
    plt.axis('off')
    plt.savefig(f"data/geotiff/wood/{gridCell}_radar.png", dpi=150, bbox_inches="tight", pad_inches=0)  
    
    plt.clf()

def main():
    addStyle()
    dataset = Dataset()
    for g in WOODSTOCK_BOXES:
        raster, record = dataset.getRaster(g)
        plotRadar(raster.read(1), g)
        plotFeatures(g)
        
if __name__ == "__main__":
    addStyle()
    dataset = Dataset()
    
    raster, record = dataset.getRaster("W08A_1")
    plotRadar(raster.read(1), "W08A_1")
    plotFeatures("W08A_1")