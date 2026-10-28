import rasterio
from scipy import ndimage

from sycamor.config.syCAMOR import WOODSTOCK_BOXES
from sycamor.visualisation.seedPlotter import plotClassified

DESPECK_SIZE = 5
def despeckle(gridCell):
    OUTDIR = "results/randomforest/run2/"
    with rasterio.open(OUTDIR+gridCell+"_rf.tif") as src:
        raster = src.read(1)
        meta = src.meta.copy()
    output_raster = OUTDIR+f"despeckle_{gridCell}_rf_size={DESPECK_SIZE}"
    despeckled_data = ndimage.median_filter(raster, size=DESPECK_SIZE)

    with rasterio.open(output_raster+".tif", "w", **meta) as dst:
        dst.write(despeckled_data, 1)
    plotClassified(despeckled_data, output_raster+".png", False)   
if __name__ == "__main__":
    for gridCell in WOODSTOCK_BOXES:
        despeckle(gridCell)