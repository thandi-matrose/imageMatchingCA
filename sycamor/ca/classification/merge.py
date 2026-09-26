import os
from pathlib import Path

import rasterio as rast

from sycamor.retrieval.dataset import Dataset
from sycamor.retrieval.utils import SAMPLE_BOXES



new_dir = "/home/thandi/HONOURS/imageMatchingCA/" 
os.chdir(new_dir)
print(f"Changed directory to: {os.getcwd()}")


def merge():
    path1 = "raster1.tif"
    path2 = "raster2.tif"
    output_path = "stacked_output.tif"

    with rast.open(path1) as src1, rast.open(path2) as src2:

        data1 = src1.read(1)
        data2 = src2.read(1)
        
    meta = src1.meta.copy()
    meta.update(count=2)

    with rast.open(output_path, "w", **meta) as dst:
        dst.write(data1, 1)  # Write first layer to band 1
        dst.write(data2, 2)  # Write second layer to band 2
def main():

    DATASET = Dataset()
    dir_path = "sycamor/ca/classification/sample/"
    output_path = "sycamor/ca/classification/merged/"
    for cell in SAMPLE_BOXES:
        raster, record = DATASET.getRaster(cell) 
        band1 = raster.read(1)
        band2 = raster.read(2)
        
        name = f"tif_{cell[1:4]}.tif" 
        file_path = os.path.join(dir_path, name)

        with rast.open(file_path) as src: 
            classBand = src.read(1)
                
        meta = raster.meta.copy()
        meta.update(count=3)
        
        with rast.open(output_path+"merge_"+cell+".tif", "w", **meta) as dst:
            dst.write(band1, 1)  
            dst.write(band2, 2)  
            dst.write(classBand, 3) 
        
main()       