from datetime import datetime

from owslib.wms import WebMapService
from owslib.map import wms130
from sycamor.retrieval.aerial.data import getOpticalData
from sycamor.retrieval.coctTiles import getTileBoxes
import rasterio as rast

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
    currBox = boxes[150]
    getImage(wms, currBox[0], currBox[1])





def getImage(wms: wms130.WebMapService_1_3_0, name:str, bbox:list):
    
    # Request the map image
    img_response = wms.getmap(
        layers=(layer_name),       # Coordinate system (e.g., EPSG:4326 for WGS 84)
        bbox=bbox,
        srs="EPSG:4326",
        size=(4000, 4000),
        format='image/tiff',
        transparent=True,
        
    )

    # 4. Save the map to a file
    output_filename = path + name +  "_COCT_"+datetime.now().strftime("%Y%m%d_%H%M%S")+".tiff"
    with open(output_filename, 'wb') as out_file:
        out_file.write(img_response.read())

    print(f"Successfully saved WMS map to {output_filename}")


if __name__ == "__main__":
    main()