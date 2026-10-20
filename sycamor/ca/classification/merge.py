import os
from pathlib import Path
import geopandas as gpd
import rasterio as rast

from sycamor.retrieval.dataset import Dataset
from sycamor.config.syCAMOR import SAMPLE_BOXES


from rasterio.warp import calculate_default_transform

new_dir = "/home/thandi/HONOURS/imageMatchingCA/" 
os.chdir(new_dir)
print(f"Changed directory to: {os.getcwd()}")

def merge():
    DATASET = Dataset()
    dir_path = "sycamor/ca/classification/sample/"
    output_path = "sycamor/ca/classification/merged/"
    for cell in SAMPLE_BOXES:
        raster, record = DATASET.getRaster(cell) 
        band1 = raster.read(1)
        band2 = raster.read(2)
        
        name = f"classes_{cell}.tif" 
        file_path = os.path.join(dir_path, name)

        with rast.open(file_path) as src: 
            classBand = src.read(1)
                
        meta = raster.meta.copy()
        meta.update(count=3)
        
        with rast.open(output_path+"merge_"+cell+".tif", "w", **meta) as dst:
            dst.write(band1, 1)  
            dst.write(band2, 2)  
            dst.write(classBand, 3) 

def main():
    optical = "data/optical/tiff/W17A_14_COCT_20260927_143223.tiff"
    with rast.open(optical, "r") as data:
        print(data.crs)
    
    shapefile = "data/shp/2024_Aerial_Imagery_1kmx1km_Grid.shp"
    gdf = gpd.read_file(shapefile)

    print(gdf.crs)
    
    print("\n\n\n\n\n")
    woodstocktiff = "data/geotiff/woodstock-salt/1km_RGB_5cm_W45A_21_0.TIF"
    with rast.open(woodstocktiff) as ref:
        print(ref.crs)
   
   
    print("THIS IS THE TRANSFORM INFO")
    
    dst_crs = 'EPSG:4326' # Web Mercator

    with rast.open(woodstocktiff) as src:
        # Calculates the ideal transform matrix, width, and height for the destination CRS
        dst_transform, dst_width, dst_height = calculate_default_transform(
            src.crs, 
            dst_crs, 
            src.width, 
            src.height, 
            *src.bounds # Unpacks (left, bottom, right, top)
        )
        
        print("New Affine Matrix:\n", dst_transform)
        print(f"Dimensions: {dst_width}x{dst_height}")
        
main()       