"""
@author Thandi Matrose




sycamor.retrieval.aerial.main
"""



from datetime import datetime
from owslib.wms import WebMapService
from owslib.map import wms130
from sycamor.config.syCAMOR import WOODSTOCK_BOXES
from sycamor.retrieval.aerial.data import getOpticalData
from sycamor.retrieval.coctTiles import getTileBoxes
import rasterio as rast
from rasterio.transform import from_bounds


layer_name = "Aerial Imagery_Aerial Imagery 2024", 
path = "data/optical/tiff/"

def main():
    df = getOpticalData()
    
    record = df.sample()
    filename = record["Filename"]
    print(filename)
    
    #name = path + filename
    name = path +"W55C_14_COCT_20260718_224346.tiff"
    print("[READ] Opening raster " , name)
    src =  rast.open(name)
    print("[DATA] Raster loaded. Raster info\n")
    print(src.meta)
    print("Spatial Resolution, X:",src.res[0])
    print("Spatial Resolution, Y:",src.res[1])
    width=src.width*src.res[0]
    height= src.height*src.res[1]
    print("Width: ", width, "m = ",width/1000," km")
    print("Height: ",height, "m = " ,height/1000,"km")
    print()
    
def wms():
    # 1. Connect to the ERDAS Apollo WMS endpoint
    apollo_wms_url = "https://cityimg.capetown.gov.za/erdas-iws/ogc/wms/GeoSpatial%20Datasets?service=WMS&request=getcapabilities&"

    # Note: ERDAS Apollo's getCapabilities usually defaults to aggregates unless WMS mode is explicitly configured in Data Manager.
    wms = WebMapService(apollo_wms_url, version="1.3.0")

    # 2. Inspect available layers
    print("Available Layers:", list(wms.contents))

    # 3. Configure the GetMap parameters
    
    boxes = getTileBoxes()
    
    for box in boxes:
        #if box[0] =="W35C_20" or box[0] =="W45A_12" or box[0] =="W57C_7" or box[0] =="W58A_15" or box[0] =="W58D_5" or box[0] =="W66D_18" or box[0] =="W55D_1" or box[0] =="W46C_7":
        #if box[0]== "W46A_11":
        if box[0] in WOODSTOCK_BOXES:
            getImage(wms, box[0], box[1])





def getImage(wms, name: str, bbox: list):
    width, height = 4000, 4000
    crs = "EPSG:4326"
    
    img_response = wms.getmap(
        layers=(layer_name),  # Ensure layer_name is accessible or passed as an argument
        bbox=bbox,
        srs=crs,
        size=(width, height),
        format='image/tiff',
        transparent=True
    )
    
    output_filename = f"{path}{name}_COCT_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tiff"
    
    raw_data = img_response.read()
    
    transform = from_bounds(bbox[0], bbox[1], bbox[2], bbox[3], width, height)
    
    with rast.MemoryFile(raw_data) as memfile:
        with memfile.open() as src:
            # Copy the profile (bands, datatype, etc.) from the source image
            profile = src.profile.copy()
            
            # Update the profile with the spatial metadata
            profile.update({
                'driver': 'GTiff',
                'height': height,
                'width': width,
                'crs': crs,
                'transform': transform
            })
            
            # Write the final georeferenced file
            with rast.open(output_filename, 'w', **profile) as dst:
                dst.write(src.read())

    print(f"Successfully saved georeferenced GeoTIFF to {output_filename}")

if __name__ == "__main__":
    wms()