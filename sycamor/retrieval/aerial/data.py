import os
import pandas as pd

def getOpticalData():
    folder_path = 'data/optical/tiff/'
      
    GRID_CELL = []
    filenames = []      
    for f in os.listdir(folder_path):
        if f.endswith('.tiff') and os.path.isfile(os.path.join(folder_path, f)):
            gridCell = f.split('_')[0] +"_" + f.split('_')[1]
            GRID_CELL.append(gridCell )
            filenames.append(f+"")
    
    data = {
        'GRID_CELL': GRID_CELL,
        'Filename': filenames
    }
    df = pd.DataFrame(data) 
    return df       
