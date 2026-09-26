

from datetime import datetime
from pathlib import Path

from matplotlib import colors, pyplot as plt
import rasterio

import numpy as np

from sycamor.ca.classification.merged.ClassifiedDataset import MERGED_DIR_PATH
from sycamor.ca.classification.scheme import LandClass
from sycamor.retrieval.utils import SAMPLE_BOXES

from pathlib import Path
import re

import os

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

def main():


    for cell in SAMPLE_BOXES:
        bands = []
        rgb = []
        with rasterio.open(MERGED_DIR_PATH+"merge_"+cell+".tif") as src:
            bands.append(src.read(1))
            bands.append(src.read(2))
            bands.append(src.read(3))
       
        pattern = rf"{cell}.*\.tiff$"
        matched_file = find_single_file_by_regex(pattern)   
        print(matched_file)
        with rasterio.open(matched_file) as src: 
            rgb.append(src.read(1))
            rgb.append(src.read(2))
            rgb.append(src.read(3))
            
        levels = [] 
        for value in LandClass.getValues():
            levels.append(value-0.5)
            
        levels.append(8.5)    
        colours =LandClass.getColours()
        print(colours)


        cmap, norm = colors.from_levels_and_colors(levels, colours)

        class_labels = LandClass.getNames()  
        class_ticks = LandClass.getValues()  


        
        fig, axes = plt.subplots(2, 2, figsize=(12, 6))
        ax1, ax2, ax3, ax4 = axes.flatten()
        im1 = ax1.imshow(np.array(rgb).transpose(1, 2, 0))
        ax1.set_title('Optical')
        ax1.axis('off') 
        
        im2 = ax2.imshow(bands[2], cmap=cmap, norm=norm, interpolation='nearest')
        ax2.set_title('Classification')
        ax2.axis('off') 
        
        cbar = fig.colorbar(im2, ax=ax2, ticks=class_ticks)
        cbar.set_ticklabels(class_labels)
        cbar.set_label('Class', fontsize=12)
        
        im3 = ax3.imshow(bands[0], cmap='viridis')
        ax3.set_title('Polarisation VV')
        
        ax3.axis('off') 
    
        im4 = ax4.imshow(bands[0], cmap='viridis')
        ax4.set_title('Polarisation VH')
        ax4.axis('off')
        
    
        plt.suptitle('Classified Radar With Aerial Results', fontsize=16, y=0.95)
        plt.savefig('results/merged/'+cell+"_"+datetime.now().strftime("%Y%m%d_%H%M%S")+"_classified.png", dpi=300, bbox_inches='tight')
             
        plt.show()
            
main()