"""
sycamor/ca/growing/region_growing.py
------------------------------------
Region-growing stage of the cellular automaton.

Starting from the seed raster, every unclassified cell combines its own
feature-based membership with inverse-distance-weighted neighbourhood
evidence, generation by generation, until no unclassified cells remain
or MAX_GENERATIONS is reached. Per-generation metrics are appended to
results/experiments/run_timesteps.csv and a one-line summary per run to
results/experiments/run_summary.csv.
"""

import csv
import json
import math
import os
import time
from datetime import datetime
from pathlib import Path

import numpy as np
import rasterio
from matplotlib import pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from PIL import Image
from scipy.ndimage import convolve

from sycamor.ca.classification.scheme import LandClass
from sycamor.ca.seed.main import openRaster
from sycamor.config.syCAMOR import (ALPHA, GROWING_CONFIDENCE_FILTER,
                                    MAX_GENERATIONS, TIME_TO_TERMINAL_VELOCITY,
                                    WINDOW, WOODSTOCK_BOXES)

SEED_DIR     = "results/seed/"
GROWING_DIR  = "results/growing/"
GIF_DIR      = "results/classification/growing/"
HEATMAP_DIR  = "results/classification/growing/"

# Inverse distance weighting
KERNEL_POWER = 2.0      # weight = distance ** -KERNEL_POWER
KERNEL_GAIN  = 1.5      # gain applied to the normalised neighbourhood mean

EXPERIMENT_SUMMARY_CSV = "results/experiments/run_summary.csv"
EXPERIMENT_STEPS_CSV   = "results/experiments/run_timesteps.csv"

RUN_SUMMARY_FIELDS = [
    "timestamp", "gridCell", "rows", "columns", "total_cells",
    "initial_classified", "final_classified", "final_unclassified",
    "generations_run", "max_generations", "classification_time_s",
    "avg_time_per_generation_s", "avg_cells_classified_per_second",
    "avg_cells_classified_per_generation", "total_new_classifications",
    "window", "kernel_power", "kernel_gain", "alpha",
    "time_to_terminal_velocity", "growing_confidence_filter",
    "class_counts_final", "class_counts_new_totals", "notes",
]
STEP_FIELDS = [
    "run_timestamp", "gridCell", "generation", "alpha_t", "step_time_s",
    "cumulative_loop_time_s", "cells_classified_this_step",
    "cumulative_classified", "remaining_unclassified", "new_per_class",
    "class_counts_after_step", "mean_confidence_above_threshold",
    "max_confidence", "ambiguous_cells_top2_margin_lt_0_05",
]


# ---------------------------------------------------------------------------
# CSV helpers
# ---------------------------------------------------------------------------
def _appendCsvRow(path, fieldnames, row):
    """Append one dict row to a CSV, writing the header the first time."""
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    new_file = not os.path.exists(path)
    with open(path, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        if new_file:
            writer.writeheader()
        writer.writerow(row)


# ---------------------------------------------------------------------------
# Neighbourhood evidence
# ---------------------------------------------------------------------------
def idw_kernel(window: int, power: float = KERNEL_POWER) -> np.ndarray:
    """Square Moore kernel with weight ||n - j||^-power; centre weight 0."""
    assert window % 2 == 1, "use an odd window so there is a true centre cell"
    c = window // 2
    y, x = np.indices((window, window))
    d = np.hypot(y - c, x - c)
    with np.errstate(divide="ignore"):
        k = 1.0 / (d ** power)
    k[d == 0] = 0.0
    return k


KERNEL = idw_kernel(WINDOW)


def neighbourhoodEvidence(membershipLayer: np.ndarray) -> np.ndarray:
    """
    IDW-weighted mean of a membership layer over the Moore neighbourhood,
    normalised by the sum of kernel weights that fall inside the raster,
    multiplied by KERNEL_GAIN and clipped to [0, 1].
    """
    m = np.asarray(membershipLayer, dtype=np.float64)
    weighted = convolve(m, KERNEL, mode="constant", cval=0.0)
    norm = convolve(np.ones_like(m), KERNEL, mode="constant", cval=0.0)
    with np.errstate(divide="ignore", invalid="ignore"):
        out = np.where(norm > 0, weighted / norm, 0.0)
    return np.minimum(out * KERNEL_GAIN, 1.0)


def alpha_quadratic_function(t: int) -> float:
    """
    Weight of neighbourhood evidence at generation t: rises quadratically
    from ALPHA at t = 0 to 1 at t = TIME_TO_TERMINAL_VELOCITY and is held
    at 1 thereafter.
    """
    t = min(t, TIME_TO_TERMINAL_VELOCITY)
    return (1 - ALPHA) * (t ** 2) / (TIME_TO_TERMINAL_VELOCITY ** 2) + ALPHA


def hexToRGB(hex_str: str):
    h = hex_str.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


# ---------------------------------------------------------------------------
# Region growing
# ---------------------------------------------------------------------------
def growing(gridCell: str, extra_meta: dict = None):
    """Grow the classification from the seed raster of `gridCell`."""
    run_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    raster = openRaster(SEED_DIR + gridCell + ".tif")
    rows, columns = raster.height, raster.width
    classed = raster.read(1).astype("uint8")

    class_list = [lc for lc in LandClass if lc.index != 0]
    # Feature-based membership per class: constant throughout the run.
    membership = {lc.index: raster.read(lc.index + 1) for lc in class_list}
    neighbourhood = {lc.index: neighbourhoodEvidence(membership[lc.index])
                     for lc in class_list}

    total_cells = rows * columns
    initial_classified = int(np.count_nonzero(classed))
    per_class_new_totals = {lc.index: 0 for lc in class_list}
    total_new, generations_run = 0, 0
    frames, step_records = [], []
    palette = np.array([hexToRGB(c) for c in LandClass.getColours()], dtype=np.uint8)

    loop_t0 = time.perf_counter()
    for t in range(MAX_GENERATIONS):
        step_t0 = time.perf_counter()
        notClassed = classed == 0
        if not notClassed.any():
            break
        generations_run = t + 1
        alpha = alpha_quadratic_function(t)

        # Combined membership of every unclassified cell in every class.
        combined = np.zeros((len(list(LandClass)), rows, columns))
        for lc in class_list:
            combined[lc.index][notClassed] = (
                (1 - alpha) * membership[lc.index][notClassed]
                + alpha * neighbourhood[lc.index][notClassed]
            )

        # Adopt the best class where it clears the threshold.
        max_values = combined.max(axis=0)
        best_class = combined.argmax(axis=0)
        adopt = max_values > GROWING_CONFIDENCE_FILTER       # False on classified cells
        prev = classed.copy()
        classed[adopt] = best_class[adopt].astype("uint8")
        frames.append(Image.fromarray(palette[classed]))

        # Per-generation metrics.
        new_mask = (classed != 0) & (prev == 0)
        n_new = int(np.count_nonzero(new_mask))
        total_new += n_new
        new_per_class = {lc.index: int(np.count_nonzero(new_mask & (classed == lc.index)))
                         for lc in class_list}
        for k, v in new_per_class.items():
            per_class_new_totals[k] += v
        class_counts = {lc.index: int(np.count_nonzero(classed == lc.index))
                        for lc in LandClass}
        sorted_vals = np.sort(combined, axis=0)
        ambiguous = int(np.count_nonzero(adopt & (sorted_vals[-1] - sorted_vals[-2] < 0.05)))

        step_records.append({
            "run_timestamp": run_timestamp, "gridCell": gridCell,
            "generation": t + 1, "alpha_t": round(alpha, 6),
            "step_time_s": round(time.perf_counter() - step_t0, 6),
            "cumulative_loop_time_s": round(time.perf_counter() - loop_t0, 6),
            "cells_classified_this_step": n_new,
            "cumulative_classified": int(np.count_nonzero(classed)),
            "remaining_unclassified": int(np.count_nonzero(classed == 0)),
            "new_per_class": json.dumps(new_per_class),
            "class_counts_after_step": json.dumps(class_counts),
            "mean_confidence_above_threshold":
                float(max_values[adopt].mean()) if adopt.any() else 0.0,
            "max_confidence": float(max_values.max()),
            "ambiguous_cells_top2_margin_lt_0_05": ambiguous,
        })

    classification_time = time.perf_counter() - loop_t0
    summary = {
        "timestamp": run_timestamp, "gridCell": gridCell,
        "rows": rows, "columns": columns, "total_cells": total_cells,
        "initial_classified": initial_classified,
        "final_classified": int(np.count_nonzero(classed)),
        "final_unclassified": int(np.count_nonzero(classed == 0)),
        "generations_run": generations_run, "max_generations": MAX_GENERATIONS,
        "classification_time_s": round(classification_time, 6),
        "avg_time_per_generation_s": round(classification_time / max(generations_run, 1), 6),
        "avg_cells_classified_per_second":
            round(total_new / classification_time, 3) if classification_time > 0 else 0.0,
        "avg_cells_classified_per_generation": round(total_new / max(generations_run, 1), 3),
        "total_new_classifications": total_new,
        "window": WINDOW, "kernel_power": KERNEL_POWER, "kernel_gain": KERNEL_GAIN,
        "alpha": ALPHA, "time_to_terminal_velocity": TIME_TO_TERMINAL_VELOCITY,
        "growing_confidence_filter": GROWING_CONFIDENCE_FILTER,
        "class_counts_final": json.dumps(
            {lc.index: int(np.count_nonzero(classed == lc.index)) for lc in LandClass}),
        "class_counts_new_totals": json.dumps(per_class_new_totals),
        "notes": "",
    }
    if extra_meta:
        summary.update(extra_meta)
    _appendCsvRow(EXPERIMENT_SUMMARY_CSV, RUN_SUMMARY_FIELDS, summary)
    for rec in step_records:
        _appendCsvRow(EXPERIMENT_STEPS_CSV, STEP_FIELDS, rec)

    # Classified raster.
    os.makedirs(GROWING_DIR, exist_ok=True)
    meta = raster.meta.copy()
    meta.update(count=1, dtype="uint8")
    with rasterio.open(GROWING_DIR + gridCell + ".tif", "w", **meta) as dst:
        dst.write(classed, 1)

    # One GIF per 200 generations.
    os.makedirs(GIF_DIR, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    chunk_size = 500
    for part in range(math.ceil(len(frames) / chunk_size)):
        chunk = frames[part * chunk_size:(part + 1) * chunk_size]
        filename = (f"{GIF_DIR}RegionGrowing_{gridCell}_{stamp}_vel-"
                    f"{TIME_TO_TERMINAL_VELOCITY}_gen-{MAX_GENERATIONS}_wind-{WINDOW}"
                    f"_alpha-{ALPHA}_part{part + 1}.gif")
        chunk[0].save(filename, save_all=True, append_images=chunk[1:],
                      duration=50, loop=0)
        print(f"Saved: {filename}")

    return summary


# ---------------------------------------------------------------------------
# Neighbourhood heatmaps (Figure: Inverse Distance Weighting Neighbourhood)
# ---------------------------------------------------------------------------
def plotNeighbourhoodHeatmaps(gridCell: str):
    raster = openRaster(SEED_DIR + gridCell + ".tif")
    os.makedirs(HEATMAP_DIR, exist_ok=True)
    for lc in LandClass:
        if lc.index == 0:
            continue
        heat = neighbourhoodEvidence(raster.read(lc.index + 1))
        cmap = LinearSegmentedColormap.from_list("custom_map", ["white", lc.colour])
        plt.imshow(heat, cmap=cmap, interpolation="none", vmin=0, vmax=1)
        plt.title("Heatmap of " + lc.displayName)
        plt.colorbar()
        plt.savefig(f"{HEATMAP_DIR}Heatmap_of_{lc.displayName}.png",
                    dpi=150, bbox_inches="tight")
        plt.close()


if __name__ == "__main__":
    for cell in WOODSTOCK_BOXES:
        growing(cell)