"""

Train a Random Forest baseline classifier on multiple optical tiles and
predict per tile, producing output rasters that align with syCAMOR and
GrowCut outputs.

Memory strategy:
  - Training: sample a fixed number of pixels per class per tile
  - Prediction: process each tile in windows, not the whole raster at once
"""
import time   
import joblib
from skimage.transform import resize
import os
import glob
import numpy as np
import pandas as pd
import rasterio
from rasterio.windows import Window
import skimage
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
import os
import re

import numpy as np
import rasterio
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

from sycamor.config.syCAMOR import SAMPLE_BOXES, WOODSTOCK_BOXES
from sycamor.retrieval.dataset import Dataset
from sycamor.visualisation.seedPlotter import plotClassified

new_dir = "/home/thandi/HONOURS/imageMatchingCA/" 
os.chdir(new_dir)
print(f"Changed directory to: {os.getcwd()}")

def getOpticalFilename(gridCell):
    path = "data/optical/tiff"
    pattern = rf"^{re.escape(gridCell)}.*\.tiff$"

    # Compile the pattern for better performance
    regex = re.compile(pattern)

    # Get all matching files
    matching_files = [
        f for f in os.listdir(path) 
        if os.path.isfile(os.path.join(path, f)) and regex.match(f)
    ]
    return path+ "/"+matching_files[0]

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
OPTICAL_DIR       = "data/optical/tiff"
CLASSIFICATION_DIR = "data/merged"
OUTPUT_DIR        = "results/randomforest/run2"
MODEL_PATH        = OUTPUT_DIR+"/rf_baseline_model.joblib"
PREDICTION_CSV    = OUTPUT_DIR + "/prediction_results.csv"

# Per-class cap for training samples from each tile.
# Prevents any single class in any single tile from dominating.
MAX_SAMPLES_PER_CLASS_PER_TILE = 2000

# Random seed for reproducibility
RANDOM_STATE = 42

# Prediction window (tile processed in strips to bound memory)
PREDICT_WINDOW = 512

os.makedirs(OUTPUT_DIR, exist_ok=True)


# ---------------------------------------------------------------------------
# 1. Discover tile pairs
# ---------------------------------------------------------------------------

def getTiles(boxes=SAMPLE_BOXES):
    tiles = []
    for box in boxes:
        opt_path = getOpticalFilename(box)
        
        cls_path = os.path.join(CLASSIFICATION_DIR, f"merge_{box}.tif")
        tiles.append((box, opt_path, cls_path))
    return tiles
# ---------------------------------------------------------------------------
# 2. Extract labelled samples from every tile
# ---------------------------------------------------------------------------
def sample_tile(opt_path, cls_path, max_per_class, rng):
    """
    Return (X, y, tile_id) where X is (n_samples, n_bands) and y is
    (n_samples,). Samples are drawn per class up to max_per_class.
    """
    with rasterio.open(opt_path) as src_opt, \
         rasterio.open(cls_path) as src_cls:

       
        # Read both rasters fully (training tiles are manageable)
        X_full = src_opt.read().astype(np.float32)   # (bands, H, W)
       
        y_full = src_cls.read(3)                     # (H, W)
        y_full = resize(
                    y_full,
                    output_shape=X_full.shape[1:],
                    anti_aliasing=False,  # Keep anti_aliasing=False for upscaling
                    order=0,  # 0: nearest, 1: bilinear, 3: bicubic, etc.
                )
        
        # Sanity check: grids must match
        if y_full.shape != X_full.shape[1:]:
            raise ValueError(
                f"Shape mismatch for {os.path.basename(opt_path)}: "
                f"optical {src_opt.shape}, classification {src_cls.shape}"
            )
    
        n_bands, H, W = X_full.shape

        # Flatten spatial dims
        X_flat = X_full.reshape(n_bands, -1).T       # (H*W, bands)
        y_flat = y_full.flatten()                    # (H*W,)

        # Sample per class
        keep_idx = []
        for cls in np.unique(y_flat):
            if cls == 0:
                continue  # skip unlabelled
            idx = np.where(y_flat == cls)[0]
            if len(idx) > max_per_class:
                idx = rng.choice(idx, size=max_per_class, replace=False)
            keep_idx.append(idx)

        if not keep_idx:
            return None, None

        keep_idx = np.concatenate(keep_idx)
        return X_flat[keep_idx], y_flat[keep_idx]

# ---------------------------------------------------------------------------
# 4. Predict per tile, in windows, preserving georeferencing
# ---------------------------------------------------------------------------
def predict_tile(clf, opt_path, out_path, window_size, tile_id=None):
    """
    Predict on a single optical tile in windows and write the result as a
    single-band uint8 GeoTIFF with the same georeferencing.

    Returns a dict summarising the prediction (class pixel counts, timing)
    so it can be logged to CSV.
    """
    t0 = time.time()
    class_counts = {}        # {class_value: pixel_count}
    total_pixels = 0

    with rasterio.open(opt_path) as src:
        profile = src.profile.copy()
        profile.update(
            dtype=rasterio.uint8,
            count=1,
            compress="lzw",
            nodata=0,
        )
        H, W = src.height, src.width

        with rasterio.open(out_path, "w", **profile) as dst:
            for row_off in range(0, H, window_size):
                h = min(window_size, H - row_off)
                for col_off in range(0, W, window_size):
                    w = min(window_size, W - col_off)
                    window = Window(col_off, row_off, w, h)

                    block = src.read(window=window).astype(np.float32)
                    n_bands, bh, bw = block.shape
                    flat = block.reshape(n_bands, -1).T

                    preds = clf.predict(flat).astype(np.uint8)
                    preds = preds.reshape(bh, bw)

                    # --- accumulate class statistics ---
                    vals, counts = np.unique(preds, return_counts=True)
                    for v, c in zip(vals, counts):
                        class_counts[int(v)] = class_counts.get(int(v), 0) + int(c)
                    total_pixels += int(preds.size)

                    dst.write(preds, 1, window=window)

    elapsed = time.time() - t0

    row = {
        "tile_id":          tile_id,
        "output_path":      out_path,
        "width":            W,
        "height":           H,
        "total_pixels":     total_pixels,
        "elapsed_seconds":  round(elapsed, 2),
    }
    # Per-class absolute + percentage columns (class_<id>_px / _pct)
    for cls, cnt in sorted(class_counts.items()):
        row[f"class_{cls}_px"]  = cnt
        row[f"class_{cls}_pct"] = round(100.0 * cnt / total_pixels, 3) \
                                  if total_pixels else 0.0

    return row


def saveModel(clf, X_train_all, y_train_all, model_path, random_state, conf, classrep):
    # 5. Save the model for reproducibility
    joblib.dump(
        {
            "model": clf,
            "n_features": X_train_all.shape[1],
            "classes": clf.classes_.tolist(),
            "random_state": random_state,
            "training_samples": len(y_train_all),
            "confusion_matrix": conf,
            "classification_report": classrep
        },
        model_path,
    )
    print(f"\nSaved model to {model_path}")

def trainModel(tiles):
    rng = np.random.default_rng(RANDOM_STATE)
    X_parts, y_parts = [], []

    for tile_id, opt_path, cls_path in tiles:
        X_t, y_t = sample_tile(
            opt_path, cls_path,
            MAX_SAMPLES_PER_CLASS_PER_TILE, rng
        )
        if X_t is None:
            print(f"  {tile_id}: no labelled pixels, skipping.")
            continue
        print(f"  {tile_id}: {len(y_t)} training samples, "
            f"classes {sorted(np.unique(y_t).tolist())}")
        X_parts.append(X_t)
        y_parts.append(y_t)

    X_train_all = np.vstack(X_parts)
    y_train_all = np.concatenate(y_parts)
    print(f"\nTotal training pool: {len(y_train_all)} samples, "
        f"{X_train_all.shape[1]} bands.")


    # ---------------------------------------------------------------------------
    # 3. Train / validation split and fit
    # ---------------------------------------------------------------------------
    X_train, X_val, y_train, y_val = train_test_split(
        X_train_all, y_train_all,
        test_size=0.3, random_state=RANDOM_STATE, stratify=y_train_all,
    )

    clf = RandomForestClassifier(
        n_estimators=300,
        max_depth=None,
        min_samples_leaf=5,
        class_weight="balanced_subsample",
        n_jobs=-1,
        random_state=RANDOM_STATE,
    )
    clf.fit(X_train, y_train)

    print("\n--- Validation performance ---")
    y_val_pred = clf.predict(X_val)
    classrep = classification_report(y_val, y_val_pred, digits=3)
    print(classrep)
    print("Confusion matrix:")
    conf = confusion_matrix(y_val, y_val_pred)
    print(conf)
      # ------------------------------------------------------------------
    prediction_rows = []

    tileWoodstock = getTiles(WOODSTOCK_BOXES)
    for tile_id, opt_path, _ in tileWoodstock:
        out_path = os.path.join(OUTPUT_DIR, f"{tile_id}_rf.tif")
        print(f"Predicting {tile_id} -> {out_path}")
        stats = predict_tile(clf, opt_path, out_path,
                             PREDICT_WINDOW, tile_id=tile_id)
        prediction_rows.append(stats)

    for tile_id, opt_path, _ in tiles:
        out_path = os.path.join(OUTPUT_DIR, f"{tile_id}_rf.tif")
        print(f"Predicting {tile_id} -> {out_path}")
        stats = predict_tile(clf, opt_path, out_path,
                             PREDICT_WINDOW, tile_id=tile_id)
        prediction_rows.append(stats)

    # ------------------------------------------------------------------
    # Write prediction summary CSV
    # ------------------------------------------------------------------
    results_df = pd.DataFrame(prediction_rows)
    results_df.to_csv(PREDICTION_CSV, index=False)
    print(f"\nSaved prediction summary to {PREDICTION_CSV}")
    print(results_df.to_string(index=False))

    saveModel(clf,X_train_all, y_train_all, MODEL_PATH, RANDOM_STATE,conf, classrep)


def main():
    TILES = getTiles()
    trainModel(TILES)

def plotRandomForest():
    for box in SAMPLE_BOXES:
        path = f'results/randomforest/run2/{box}_rf.tif'
        with rasterio.open(path) as src:
            img = src.read(1)
        plotClassified(img, f"results/randomforest/run2/{box}_rf.png", False)
    for box in WOODSTOCK_BOXES:
            path = f'results/randomforest/run2/{box}_rf.tif'
            with rasterio.open(path) as src:
                img = src.read(1)
            plotClassified(img, f"results/randomforest/run2/{box}_rf.png", False)
if __name__ == "__main__":
    plotRandomForest()