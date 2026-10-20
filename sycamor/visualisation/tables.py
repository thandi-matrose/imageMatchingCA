import os

import geopandas as gpd
import numpy as np
import pandas as pd

from sycamor.config.syCAMOR import WOODSTOCK_BOXES
from sycamor.visualisation.plot import writeTable
new_dir = "/home/thandi/HONOURS/imageMatchingCA/" 
os.chdir(new_dir)
print(f"Changed directory to: {os.getcwd()}")



def exportDistTable():
    path = "data/shp/DistanceToStudyArea.shp"
    sampleDf = gpd.read_file(path)
    
    sampleDf['COCT Grid Cell'] = sampleDf['GRID_CELL'].str.replace("_", r"\_", regex=False)

    sampleDf['X (m)'] = sampleDf['X_coord'].map('{:,.0f}'.format).str.replace(',', ' ')
    sampleDf['Y (m)'] = sampleDf['Y_coord'].map('{:,.0f}'.format).str.replace(',', ' ')
    sampleDf['Distance (m)'] = sampleDf['distance'].map('{:,.3f}'.format).str.replace(',', ' ').replace("_", rf"\_")
    sampleDf = sampleDf.sort_values(by='distance')
    sampleDf = sampleDf[["COCT Grid Cell", 'X (m)', 'Y (m)', "Distance (m)"]]
   
    print(sampleDf)
    writeTable(sampleDf,"training_cells", "Spatial Information pertaining to Training Data Grid Cells", index=False, column_format="lrrr")

def exportGridBasedSeedTables():
    df = pd.read_csv("results/seed/stats.csv")
    
    df = df.rename(columns={"GRID_CELL": 'Grid Cell', "Class":"Land Class"})
    df['Pixel'] = df['Pixel'].str.replace(',', '').astype(int)
    for cell in WOODSTOCK_BOXES:
        subset = df[df['Grid Cell'] == cell]
        total_pixels = subset['Pixel'].sum()

        # Filter for 'Undefined' land class and sum only the 'Pixel' column
        total_seeded = subset[subset['Land Class'] != 'Undefined']['Pixel'].sum()
        # Check if subset is empty to avoid division by zero or empty prints
        if not subset.empty:
            subset['Percent of Total Pixels'] = (subset['Pixel'] / total_pixels*100).round(3)
            
            subset.loc[subset['Land Class'] == 'Undefined', 'Percent of Total Seeded'] = 0
            
            # 3. Correct the assignments using the pre-calculated scalar totals
            subset['Percent of Total Seeded'] = ((subset['Pixel'] / total_seeded*100)).round(3)
            
            subset.loc['Total'] = subset.select_dtypes(include='number').sum().round(2)
            subset.fillna("-", inplace=True)
            subset.replace(99.999, 100)
            subset["Grid Cell"] = subset["Grid Cell"].astype(str).str.replace("_", r"\_", regex=False)
            subset.loc['Total',"Land Class"] = "Total"
            subset = subset[["Land Class", "Pixel", "Percent of Total Seeded", "Percent of Total Pixels"]]
        writeTable(subset, f"training_stats_{cell}", f"Seeding Statistics for Grid Cell {cell}".replace("_", r"\_"), index=False, column_format="llrrr")

    print(df)
def exportSeedingStats():
    df = pd.read_csv("results/seed/stats.csv")
    
    df = df.rename(columns={"GRID_CELL": 'Grid Cell', "Class":"Land Class"})
    df = df[df["Land Class"]!="Undefined"]
    df['Pixel'] = df['Pixel'].str.replace(',', '').astype(int)
    result = df.groupby('Grid Cell')[['Pixel']].sum() 
    result['Percent of Total Raster'] = ((result['Pixel'] / 66050*100)).round(3)
    result.loc['Average'] = result["Percent of Total Raster"].mean().round(2)
    result.loc['Median'] = result["Percent of Total Raster"].median().round(2)
    result.loc['Min'] = result["Percent of Total Raster"].min().round(2)
    result.loc['Max'] = result["Percent of Total Raster"].max().round(2)
    result.loc['Average',"Pixel"] = 0.0
    result.loc['Median',"Pixel"] = 0.0
    result.loc['Min',"Pixel"] = 0.0
    result.loc['Max',"Pixel"] = 0.0
    result['Pixel'] = result['Pixel'].astype(int)
    result.index = result.index.astype(str).str.replace("_", r"\_", regex=False)
                
    writeTable(result, f"seeding_stats", f"Seeding Statistics".replace("_", r"\_"), index=True, column_format="lrr")
def exportSeedingProcessing():
    
    df = pd.read_csv("results/seed/time.csv")
    print(df)
if __name__ == "__main__":
    exportSeedingProcessing()