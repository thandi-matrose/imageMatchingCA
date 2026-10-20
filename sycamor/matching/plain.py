from matplotlib import pyplot as plt
import scipy
from skimage.registration import phase_cross_correlation
import rasterio
import numpy as np

from skimage.transform import resize
    
from skimage import color, io
import numpy as np
import scipy.ndimage
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, BoundaryNorm
from matplotlib.patches import FancyArrowPatch
import rasterio
from skimage.transform import resize
from skimage.registration import phase_cross_correlation
from mpl_toolkits.axes_grid1 import make_axes_locatable

from sycamor.ca.classification.scheme import LandClass
from sycamor.matching.main import match
from sycamor.visualisation.plot import addStyle
from sycamor.visualisation.seedPlotter import plotClassified


def main():
    img = io.imread('data/optical/tiff/W35C_20_COCT_20260925_011627.tiff')
    if img.shape[-1] == 4:
        img = img[:, :, :3]
    img1 = color.rgb2gray(img)

    
    with rasterio.open("data/radar/hart94/W35C_20_HART94_20260713_110318.tiff") as src:
        img2 = src.read(1)
    
    img2 = resize(
                img2,
                output_shape=img1.shape,
                anti_aliasing=False, 
                order=1,  # 0: nearest, 1: bilinear, 3: bicubic, etc.
            )
    match(img1, img2, img2, gridCell="W35C_20", output_path="results/matching/plainTest.png")
if __name__ == "__main__":
    main()
    