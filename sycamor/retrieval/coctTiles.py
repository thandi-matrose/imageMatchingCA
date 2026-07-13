import geopandas as gpd
from sycamor.retrieval import datasetManager, interface, utils


def getImage(box, hub, dataManager, name = "img"):
    request = hub.createRequest(boundingBox=box)
    data = hub.sendRequest(request)
    
    print("Encoding" + str(data.apparent_encoding))
    print("Content:" + str(data.content))
    print("Headers:" + str(data.headers))
    print("Status Code:" + str(data.status_code))
    
    images = data.content
    count = 0
    dataManager.writeImage(images, name+"_"+str(count)+"_")

    count+=1
    
def getTileBoxes():
    gdf =  gpd.read_file("data/shp/2024_Aerial_Imagery_1kmx1km_Grid.shp")
    epsg = utils.EPSG
    print(gdf.crs)
    
    #Convert CRS to EPSG 4326
    gdf = gdf.to_crs(epsg)
    print("study area crs",str(gdf.crs))
    
    b = gdf.total_bounds  
    bounds = list(map(float, b))
    print("Total Bounds:", bounds)
    
    tileBoxes = []
    for index, row in gdf.iterrows():
        print(row) 
        feature_name = row['GRID_CELL'] 
        
        geometry = row['geometry']
        bounds = geometry.bounds 
        
        
        bounds = list(map(float, bounds))
        
        tileBoxes.append((feature_name,  bounds))
        
    return tileBoxes

def getRandomBoundingBoxes(studyArea) :
    
    boundingBox = studyArea.getBounds(epsg=utils.EPSG)
   
    print(boundingBox)
    print("Top: " + str(boundingBox[3]))
    print("Bottom: " + str(boundingBox[1]))
    print("Left: " + str(boundingBox[0]))
    print("Right: " + str(boundingBox[2]))
    
    top = boundingBox[3]
    bottom = boundingBox[1]
    left = boundingBox[0]
    right = boundingBox[2]
    
    heightDivisor = 25
    widthDivisor = 25
    
    heightRange = (bottom-top)/heightDivisor
    widthRange = (right-left)/widthDivisor
    
    boundingBoxes = []
    
    for i in range(heightDivisor):
        newTop = top + i*heightRange
        newBottom = top + (i+1)*heightRange
        for j in range(widthDivisor):
            newLeft = left + j*widthRange
            newRight = left + (j+1)*widthRange
            newBox = [float(newLeft), float(newBottom), float(newRight), float(newTop)]
            boundingBoxes.append(newBox)
            print((newBox))
         
    
    print(boundingBoxes)
    
    return boundingBoxes
    
def main():
    print("Image Matching CA")
    print("-"*25)
    hub = interface.SentinelHub()
    dataManager = datasetManager.DatasetManager()
    
    boxes = getTileBoxes()
    
    with open('data/radar/bounds.txt', 'w') as file:
        file.write(str(boxes))
   
    for i in range(len(boxes)):
        getImage(boxes[i][1], hub, dataManager, boxes[i][0])