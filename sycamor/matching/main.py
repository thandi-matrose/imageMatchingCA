import os

from matplotlib import pyplot as plt
import scipy
from skimage.registration import phase_cross_correlation
import rasterio
import numpy as np

from skimage.transform import resize
    
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
from sycamor.config.syCAMOR import SAMPLE_BOXES, WOODSTOCK_BOXES
from sycamor.retrieval.dataset import Dataset
from sycamor.visualisation.plot import addStyle
from sycamor.visualisation.seedPlotter import plotClassified
new_dir = "/home/thandi/HONOURS/imageMatchingCA/" 
os.chdir(new_dir)
print(f"Changed directory to: {os.getcwd()}")
def match(img1, img2, img3, gridCell,
          output_path: str | None = None,
          dpi: int = 200,
          figsize: tuple = (16, 10)):
     

    # Detect the shift between them
    shift, error, diffphase = phase_cross_correlation(img1, img2, upsample_factor=1)

    print(f"Detected shift (y, x): {shift}")
    print(f"Registration error: {error}")
    
    image_fft = np.fft.fft2(img3)
    matched_fft = scipy.ndimage.fourier_shift(image_fft, shift, n=-1, axis=-1, output=None)
    matchedImg = np.fft.ifft2(matched_fft).real
    path = f"results/matching/{gridCell}.png"
    #plotClassified(matchedImg, path)
    plt.imshow(matchedImg)
    plt.show()
    
    plot(gridCell, figsize, img1, img2, shift, matchedImg, output_path, error, dpi, diffphase)




# ---------------------------------------------------------------------------
# Build a discrete colormap from the LandClass enum
# ---------------------------------------------------------------------------
def build_class_colormap():
    """
    Return (cmap, norm) for the seven syCAMOR classes plus an
    UNDEFINED grey at index 0.
    """
    # Sort classes by index
    classes = sorted(LandClass, key=lambda c: c.index)
    colours = [c.colour if c.index != 0 else "#3a3a3a" for c in classes]
    cmap = ListedColormap(colours)
    # Boundaries at 0.5, 1.5, ..., n-0.5 so that integer index i
    # maps to the i-th colour
    boundaries = np.arange(-0.5, len(classes) + 0.5, 1)
    norm = BoundaryNorm(boundaries, cmap.N)
    return cmap, norm


CLASS_CMAP, CLASS_NORM = build_class_colormap()


# ---------------------------------------------------------------------------
# Main visualisation function
# ---------------------------------------------------------------------------
def matchOld(gridCell: str,
          radar_path: str | None = None,
          output_path: str | None = None,
          dpi: int = 200,
          figsize: tuple = (16, 10)):
    """
    Match a GrowCut classification to a Random Forest baseline, apply
    the detected shift to the source radar imagery, and produce a
    four-panel figure.

    Parameters
    ----------
    gridCell : str
        Tile identifier, e.g. "W35C_20".
    radar_path : str or None
        Path to the raw radar GeoTIFF. If None, defaults to the
        HART94 product path used in the original function.
    output_path : str or None
        If provided, the figure is saved here.
    dpi : int
        Figure resolution for saving.
    figsize : tuple
        Figure size in inches.

    Returns
    -------
    dict with keys:
        shift, error, diffphase, matchedImg
    """
    # ---------------------------------------------------------------------
    # 1. Load classified rasters
    # ---------------------------------------------------------------------
    rf_path     = f"results/randomforest/{gridCell}_rf.tif"
    growcut_path = f"results/growcut/{gridCell}.tif"

    with rasterio.open(rf_path) as opt:
        rf_img = opt.read(1)
    with rasterio.open(growcut_path) as radar:
        growcut_img = radar.read(1)

    # Resize GrowCut to match RF grid
    growcut_img = resize(
        growcut_img,
        output_shape=rf_img.shape,
        anti_aliasing=False,
        order=1,        # bilinear
        preserve_range=True,
    ).astype(np.int32)

    # ---------------------------------------------------------------------
    # 2. Detect shift
    # ---------------------------------------------------------------------
    shift, error, diffphase = phase_cross_correlation(
        rf_img, growcut_img, upsample_factor=10
    )
    print(f"Detected shift (y, x): {shift}")
    print(f"Registration error:    {error:.4f}")
    print(f"Diff phase:            {diffphase:.4f}")

    # ---------------------------------------------------------------------
    # 3. Load radar and apply the shift via Fourier shift
    # ---------------------------------------------------------------------
    if radar_path is None:
        radar_path = "data/radar/hart94/W35C_20_HART94_20260713_110318.tiff"

    with rasterio.open(radar_path) as src:
        radar_img = src.read(1).astype(np.float32)

    # Resize radar to match RF grid (for aligned comparison)
    if radar_img.shape != rf_img.shape:
        radar_img = resize(
            radar_img,
            output_shape=rf_img.shape,
            anti_aliasing=True,
            preserve_range=True,
        ).astype(np.float32)

    # Fourier shift
    image_fft = np.fft.fft2(radar_img)
    shifted_fft = scipy.ndimage.fourier_shift(image_fft, shift)
    matchedImg = np.fft.ifft2(shifted_fft).real
    

def plot(gridCell, figsize, rf_img, growcut_img, shift, matchedImg, output_path, error, dpi, diff_phase):  
    fig = plt.figure(figsize=figsize, constrained_layout=True)

    # Grid: 2 rows x 3 cols
    #   [ RF  ] [ GrowCut ] [ Radar (shifted) ]
    #   [ Diff ] [ Shift arrow inset ] [ Matched overlay ]
    gs = fig.add_gridspec(
        2, 3,
        height_ratios=[1, 0.05],
        hspace=0.05,
        wspace=0.10,
    )

    ax_rf      = fig.add_subplot(gs[0, 0])
    ax_gc      = fig.add_subplot(gs[0, 1])
    ax_shift   = fig.add_subplot(gs[0, 2])
    ax_legend  = fig.add_subplot(gs[1, :])

    # ---------------------------------------------------------------------
    # Panel A: Random Forest classification
    # ---------------------------------------------------------------------
    im_rf = ax_rf.imshow(rf_img, cmap=CLASS_CMAP, norm=CLASS_NORM,
                         interpolation="nearest")
    ax_rf.set_title("(a) Random Forest baseline",
                    fontsize=13, fontweight="bold", pad=10)
    ax_rf.set_xticks([]); ax_rf.set_yticks([])
    _add_scalebar(ax_rf, rf_img.shape, pixel_size_m=0.05, label="50 m")

    # ---------------------------------------------------------------------
    # Panel B: GrowCut classification
    # ---------------------------------------------------------------------
    im_gc = ax_gc.imshow(growcut_img, cmap=CLASS_CMAP, norm=CLASS_NORM,
                         interpolation="nearest")
    ax_gc.set_title("(b) GrowCut classification",
                    fontsize=13, fontweight="bold", pad=10)
    ax_gc.set_xticks([]); ax_gc.set_yticks([])
    _add_scalebar(ax_gc, growcut_img.shape, pixel_size_m=0.05, label="50 m")

    # Annotate the detected shift between the two panels
    _annotate_shift(ax_gc, shift)

    # ---------------------------------------------------------------------
    # Panel C: Radar image before and after shift
    # ---------------------------------------------------------------------
    # Show the radar image with a semi-transparent overlay of where it
    # was before (dashed white outline) and where it is after (solid).
    ax_shift.imshow(matchedImg, cmap="gray", interpolation="bilinear")
    ax_shift.set_title("(c) Radar after applied shift",
                       fontsize=13, fontweight="bold", pad=10)
    ax_shift.set_xticks([]); ax_shift.set_yticks([])

    # Overlay the RF classification boundaries as thin white contours
    _overlay_boundaries(ax_shift, rf_img, colour="cyan", linewidth=0.4, alpha=0.7)

    # Draw an arrow indicating the applied shift
    _draw_shift_arrow(ax_shift, shift)

    # ---------------------------------------------------------------------
    # Shared legend
    # ---------------------------------------------------------------------
    _draw_legend(ax_legend)

    # ---------------------------------------------------------------------
    # Suptitle and metadata
    # ---------------------------------------------------------------------
    fig.suptitle(
        f"syCAMOR Matching — Tile {gridCell}",
        fontsize=15, fontweight="bold", y=1.02,
    )
    fig.text(
        0.5, -0.02,
        rf"Detected shift:  y = {shift[0]:+.2f} px, "
        rf"x = {shift[1]:+.2f} px    |    "
        f"Registration error: {error:.4f}",
        ha="center", fontsize=11, style="italic", color="#444444",
    )

    # ---------------------------------------------------------------------
    # Save
    # ---------------------------------------------------------------------
    if output_path is not None:
        fig.savefig(output_path, dpi=dpi, bbox_inches="tight",
                    facecolor="white")
        print(f"Saved {output_path}")

    plt.show()

    return {
        "shift": shift,
        "error": error,
        "diffphase": diff_phase,
        "matchedImg": matchedImg,
    }


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------
def _add_scalebar(ax, shape, pixel_size_m, label):
    """Draw a simple scalebar in the lower-left corner."""
    h, w = shape
    bar_px = int(50 / pixel_size_m) if pixel_size_m < 1 else 50
    x0 = int(w * 0.05)
    y0 = int(h * 0.95)
    ax.plot([x0, x0 + bar_px], [y0, y0], color="white",
            linewidth=4, solid_capstyle="butt")
    ax.plot([x0, x0 + bar_px], [y0, y0], color="black",
            linewidth=2, solid_capstyle="butt")
    ax.text(x0 + bar_px / 2, y0 - h * 0.02, label,
            color="white", fontsize=8, ha="center", va="bottom",
            fontweight="bold",
            bbox=dict(facecolor="black", alpha=0.5, pad=2, edgecolor="none"))


def _annotate_shift(ax, shift):
    """Draw a compact shift annotation box on the panel."""
    dy, dx = shift
    text = rf"y = {dy:+.2f} px\\x= {dx:+.2f} px"
    ax.text(
        0.98, 0.02, text,
        transform=ax.transAxes,
        ha="right", va="bottom",
        fontsize=10, family="monospace",
        bbox=dict(facecolor="white", alpha=0.85,
                  edgecolor="#666666", boxstyle="round,pad=0.4"),
    )


def _draw_shift_arrow(ax, shift):
    """Draw an arrow from the un-shifted position to the shifted one."""
    dy, dx = shift
    # Place the arrow in the centre of the panel
    x_start, y_start = 0.5, 0.5
    x_end   = x_start + dx / 500
    y_end   = y_start + dy / 500
    arrow = FancyArrowPatch(
        (x_start, y_start), (x_end, y_end),
        transform=ax.transAxes,
        arrowstyle="-|>", mutation_scale=20,
        color="red", linewidth=2.5, alpha=0.9,
    )
    ax.add_patch(arrow)


def _overlay_boundaries(ax, label_img, colour="white", linewidth=0.5, alpha=0.6):
    """Draw class boundaries as a contour overlay."""
    # Detect boundaries via a simple 4-neighbour difference
    gy, gx = np.gradient(label_img.astype(float))
    edges = (np.abs(gx) > 0) | (np.abs(gy) > 0)
    ax.contour(
        edges, levels=[0.5],
        colors=colour, linewidths=linewidth, alpha=alpha,
    )


def _draw_legend(ax):
    """Draw a horizontal legend showing all classes."""
    classes = sorted(LandClass, key=lambda c: c.index)
    handles = []
    for c in classes:
        from matplotlib.patches import Patch
        handles.append(Patch(
            facecolor=c.colour if c.index != 0 else "#3a3a3a",
            edgecolor="#333333",
            label=f"{c.index}: {c.displayName}",
        ))
    ax.axis("off")
    ax.legend(
        handles=handles,
        loc="center", ncol=len(classes),
        frameon=False, fontsize=10,
        handlelength=1.5, handleheight=1.0,
        columnspacing=1.2,
    )

def main():
    addStyle()
    
    for gridCell in ["W45C_12"]:
    # Load two classified rasters
        with rasterio.open(f'results/randomforest/run2/despeckle_{gridCell}_rf_size=5.tif') as opt, \
            rasterio.open(f'results/growcut/otherwoodstock/{gridCell}.tif') as radar:
            img1 = opt.read(1)
            img2 = radar.read(1)
            img2 = resize(
                    img2,
                    output_shape=img1.shape,
                    anti_aliasing=False, 
                    order=0,  # 0: nearest, 1: bilinear, 3: bicubic, etc.
                )
            
        dataset = Dataset()
        raster, record = dataset.getRaster(gridCell)
        img3 = raster.read(1)
        img3 = resize(
                            img3,
                            output_shape=img1.shape,
                            anti_aliasing=False, 
                            order=0,  # 0: nearest, 1: bilinear, 3: bicubic, etc.
                        )
        
        result = match(img1, img2, img3,
                    gridCell=gridCell,
                    output_path=f"results/matching/{gridCell}_match.png",
                    dpi=200,
                )
        
        print(np.max(img2))
                
    #print(f"\nResult max value: {result['matchedImg'].max():.2f}")

if __name__ == "__main__":
    main()