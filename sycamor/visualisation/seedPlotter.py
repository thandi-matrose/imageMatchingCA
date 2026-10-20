

import csv
from datetime import datetime
import math
from pathlib import Path

from matplotlib import colors, pyplot as plt
import pandas as pd
import rasterio

from matplotlib import colors as mcolors
import numpy as np
from sycamor.ca.classification.scheme import LandClass

from pathlib import Path
import re

import os

from sycamor.config.syCAMOR import  SAMPLE_BOXES, WOODSTOCK_BOXES
from sycamor.visualisation.plot import addStyle

new_dir = "/home/thandi/HONOURS/imageMatchingCA/" 
os.chdir(new_dir)
print(f"Changed directory to: {os.getcwd()}")

aerial_dir_path = "data/optical/tiff/"

addStyle()
def find_single_file_by_regex( regex_pattern):
    compiled_regex = re.compile(regex_pattern)
    for path in Path(aerial_dir_path).iterdir():
        
        if path.is_file() and compiled_regex.search(path.name):

            return path 
            
    return None

def plotClassified(band, filename="", legend=True):
   
    
        
    levels = [] 
    for value in LandClass.getValues():
        levels.append(value-0.5)
        
    levels.append(8.5)    
    colours =LandClass.getColours()
    print(colours)


    cmap, norm = colors.from_levels_and_colors(levels, colours)

    class_labels = LandClass.getNames()  
    class_ticks = LandClass.getValues()  


    plt.figure(figsize=(10, 6))

    # 2. Plot the image
    im = plt.imshow(band, cmap=cmap, norm=norm, interpolation='nearest')

    plt.axis('off')

    if (legend):
        # 4. Add the colorbar using the current figure and current axes (plt.gca())
        cbar = plt.colorbar(im, ax=plt.gca(), ticks=class_ticks)
        cbar.set_ticklabels(class_labels)
    
    if filename == "":
        plt.savefig('results/classification/growing/'+"Classified"+"_"+datetime.now().strftime("%Y%m%d_%H%M%S")+"_classified.png", dpi=300, bbox_inches='tight')
    else:
        plt.savefig(filename, dpi=300, bbox_inches='tight')   

def plotTrainingSeeds():
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
        with rasterio.open(f"results/seed/{cell}.tif") as src:
            band=src.read(1)
        im = ax.imshow(band, cmap=cmap, norm=norm, interpolation='nearest')
        ax.text(10,20, cell,zorder=5)
   
    '''
    cbar = plt.colorbar(im, ax=plt.gca(), ticks=class_ticks)
    cbar.set_ticklabels(class_labels)
    cbar.set_label('Class', fontsize=12)
    '''
    plt.savefig('results/seed/res/'+f"allSeed"+"_"+datetime.now().strftime("%Y%m%d_%H%M%S")+".png", dpi=300, bbox_inches='tight')
    
    ax.clear()   
def plotSeed(cell, filename="", title=""):
    
    band = []
    rgb = []
    with rasterio.open(f"results/seed/{cell}.tif") as src:
        band=src.read(1)
    unique, counts = np.unique(band, return_counts=True)
    counts_dict = dict(zip(unique, counts))

    indices      = np.delete(LandClass.getIndices(), 0)
    values_all   = LandClass.getValues()
    colours_all  = LandClass.getColours()
    names        = np.delete(LandClass.getNames(),   0)
    colours_kept = np.delete(colours_all,            0)

    class_counts = np.array([counts_dict.get(i, 0) for i in indices], dtype=int)
    total_seeded = int(class_counts.sum())
    total_pixels = band.size
    unseeded     = total_pixels - total_seeded +1
    
    
    
 
    levels = [] 
    for value in LandClass.getValues():
        levels.append(value-0.5)
        
    levels.append(8.5)    
    colours =LandClass.getColours()
    names = np.delete(LandClass.getNames(), 0)
    row_colours = np.delete(LandClass.getColours(), 0)


    cmap, norm = colors.from_levels_and_colors(levels, colours)

    class_labels = LandClass.getNames()  
    class_ticks = LandClass.getValues()  

    plt.figure(figsize=(10, 6))

    # 2. Plot the image
    im = plt.imshow(band, cmap=cmap, norm=norm, interpolation='nearest')

    # 3. Modify axes properties directly using plt
    ax = plt.gca()
    cell_text = [[name, disp] for name, disp in zip(names, counts)]
    col_headers = ["Class Name", "Count"]

    ax.text(10,10,cell)
   
    rows = []
    headers = ["GRID_CELL","Class", "Pixels"]

    for nm, cnt, col in zip(names, class_counts, colours_kept):
        pct = 100 * cnt / total_seeded if total_seeded else 0.0
        rows.append([cell, nm, f"{cnt:,}"])

    
    rows.append([cell, "Undefined",     f"{unseeded:,}"])
    df = pd.DataFrame(rows, columns=headers)
    
    widths = [0.55, 0.25, 0.2]
    
    #writeSeedInfo(rows)
    
    # 4. Add the colorbar using the current figure and current axes (plt.gca())
    '''
    cbar = plt.colorbar(im, ax=plt.gca(), ticks=class_ticks)
    cbar.set_ticklabels(class_labels)
    cbar.set_label('Class', fontsize=12)
    '''
    if (filename==""):
        plt.savefig('results/seed/res/'+f"{cell}"+"_"+datetime.now().strftime("%Y%m%d_%H%M%S")+".png", dpi=300, bbox_inches='tight')
    else:
        plt.savefig(filename, dpi=300, bbox_inches='tight')
    ax.clear() 
def writeSeedInfo(data):
    with open("results/seed/stats.csv", "a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerows(data)                         
def plotSeedWithTable(cell, filename="", title=""):

    band = []
    rgb = []
    with rasterio.open(f"results/seed/{cell}.tif") as src:
        band=src.read(1)
    unique, counts = np.unique(band, return_counts=True)
    counts_dict = dict(zip(unique, counts))

    indices      = np.delete(LandClass.getIndices(), 0)
    values_all   = LandClass.getValues()
    colours_all  = LandClass.getColours()
    names        = np.delete(LandClass.getNames(),   0)
    colours_kept = np.delete(colours_all,            0)

    class_counts = np.array([counts_dict.get(i, 0) for i in indices], dtype=int)
    total_seeded = int(class_counts.sum())
    total_pixels = band.size
    unseeded     = total_pixels - total_seeded +1
    
    
    
 
    levels = [] 
    for value in LandClass.getValues():
        levels.append(value-0.5)
        
    levels.append(8.5)    
    colours =LandClass.getColours()
    names = np.delete(LandClass.getNames(), 0)
    row_colours = np.delete(LandClass.getColours(), 0)


    cmap, norm = colors.from_levels_and_colors(levels, colours)

    class_labels = LandClass.getNames()  
    class_ticks = LandClass.getValues()  

    plt.figure(figsize=(10, 6))

    # 2. Plot the image
    im = plt.imshow(band, cmap=cmap, norm=norm, interpolation='nearest')

    # 3. Modify axes properties directly using plt
    ax = plt.gca()
    cell_text = [[name, disp] for name, disp in zip(names, counts)]
    col_headers = ["Class Name", "Count"]

    ax.set_title( "Classification Seeds of "+ cell)
   
    rows = []
    for nm, cnt, col in zip(names, class_counts, colours_kept):
        pct = 100 * cnt / total_seeded if total_seeded else 0.0
        rows.append([nm, f"{cnt:,}", rf"{pct:5.1f}\%"])

    rows.append(["Total seeded", f"{total_seeded:,}", "100.0%"])
    rows.append(["",     f"",     ""])
    rows.append(["Unseeded",     f"{unseeded:,}",     ""])

    rows.append(["Seeded",  f"{str(total_seeded)}/{str(unseeded+total_seeded)}",    f"{round(total_seeded/(unseeded+total_seeded)*100, 3)}\%"])
    headers = ["Class", "Pixels", r"\% of seeds"]
    widths = [0.55, 0.25, 0.2]
    tbl = ax.table(
        cellText=rows,
        colLabels=headers,
        cellLoc="right",
        colLoc="center",
        colWidths=widths,
        bbox=[1.02,0.25,0.65,0.5]
    )
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(9)
    # --- header row ---
    for c in range(len(headers)):
        cell_ = tbl[0, c]
        cell_.set_facecolor("#ffffff")
        cell_.set_text_props(color="black", weight="bold")
        cell_.set_edgecolor("white")

    # --- body rows ---
    for r, colour in enumerate(colours_kept, start=1):
        name_cell = tbl[r, 0]
        name_cell.set_facecolor(colour)
        name_cell.set_edgecolor("black")

        r_, g_, b_ = mcolors.to_rgb(colour)
        lum = 0.2126 * r_ + 0.7152 * g_ + 0.0722 * b_
        name_cell.set_text_props(color="black" if lum > 0.6 else "white",
                                    weight="bold")

        shade = "#f7f7f7" if r % 2 == 0 else "white"
        for c in (1, 2):
            tbl[r, c].set_facecolor(shade)
            tbl[r, c].set_edgecolor("black")
    
    # 4. Add the colorbar using the current figure and current axes (plt.gca())
    '''
    cbar = plt.colorbar(im, ax=plt.gca(), ticks=class_ticks)
    cbar.set_ticklabels(class_labels)
    cbar.set_label('Class', fontsize=12)
    '''
    if (filename==""):
        plt.savefig('results/seed/res/'+f"{cell}"+"_"+datetime.now().strftime("%Y%m%d_%H%M%S")+".png", dpi=300, bbox_inches='tight')
    else:
        plt.savefig(filename, dpi=300, bbox_inches='tight')
    ax.clear()          
def rf():
    for box in SAMPLE_BOXES:
        with rasterio.open(f"results/randomforest/{box}_rf.tif") as src:
            plotClassified(src.read(1), f"results/randomforest/{box}_rf.png")
            
if __name__ == "__main__":
    for cell in WOODSTOCK_BOXES:
        with rasterio.open(f"results/growcut/woodstock/{cell}.tif") as src:
            band = src.read(1)
            plotClassified(band,legend= False)