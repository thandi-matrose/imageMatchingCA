import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import numpy as np
import rasterio
from matplotlib import colors
import os
from sycamor.ca.classification.scheme import LandClass
from pathlib import Path


new_dir = "/home/thandi/HONOURS/imageMatchingCA/" 
os.chdir(new_dir)
print(f"Changed directory to: {os.getcwd()}")




dir_path = Path("sycamor/ca/classification/sample/")

classified_tif_files = [str(f) for f in dir_path.glob("*") if f.suffix.lower() in [".tif"]]

raster_list = []

for raster in classified_tif_files:
    with rasterio.open(raster) as src:
        raster_list.append(src.read(1))

print(len(classified_tif_files))

levels = [] 
max = 0;
for value in LandClass.getValues():
    levels.append(value-0.5)
    
levels.append(8.5)    
colours =LandClass.getColours()

cmap, norm = colors.from_levels_and_colors(levels, colours)

class_labels = LandClass.getNames()  
class_ticks = LandClass.getValues()  


fig, axes = plt.subplots(3, 3, figsize=(18, 10), sharex=True, sharey=True)

axes_flat = axes.flatten()

for i, ax in enumerate(axes_flat):
    raster_data = raster_list[i] 
    
    im = ax.imshow(raster_data, cmap=cmap, norm=norm, interpolation='nearest')
    
    ax.set_title(f'Plot {i+1}', fontsize=10)
    ax.axis('off')

fig.subplots_adjust(right=0.85)
cbar_ax = fig.add_axes([0.88, 0.15, 0.02, 0.7]) 

cbar = fig.colorbar(im, cax=cbar_ax, ticks=class_ticks)
cbar.set_ticklabels(class_labels)
cbar.set_label('Class', fontsize=12)

plt.suptitle('Classified Grid Results', fontsize=16, y=0.95)
plt.show()