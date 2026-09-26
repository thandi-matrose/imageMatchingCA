

from datetime import datetime
import os

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.lines import Line2D

from sycamor.ca.classification.scheme import LandClass
from sycamor.ca.features.set import Feature
from sycamor.visualisation.plot import addStyle

addStyle()

new_dir = "/home/thandi/HONOURS/imageMatchingCA/" 
os.chdir(new_dir)
print(f"Changed directory to: {os.getcwd()}")

CSV_PATH = "results/records/data.csv"

CSV_TO_FEATURE = {
    "log_intensity":  Feature.LOG_INTENSITY,
    "speck_diverge":  Feature.SPECKLE_DIVERGENCE,
    "glcm_energy":    Feature.ENERGY_GLCM,
    "glcm_mean":      Feature.MEAN_GLCM,
    "glcm_variance":  Feature.VARIANCE_GLCM,
}

FEATURES = list(CSV_TO_FEATURE.values())

CLASS_COLOURS = {c.index: c.colour for c in LandClass}
CLASS_LABELS  = {c.index: c.displayName for c in LandClass}

# Exclude UNDEFINED from most plots
PLOTTABLE_CLASSES = [c.index for c in LandClass if c.index != 0]


POLARISATION_COLOURS = {"VV": "#1f77b4", "VH": "#ff7f0e"}

OUTPUT_DIR = "results/classification"

df = pd.read_csv(CSV_PATH)
df = df.rename(columns={df.columns[0]: "timestamp"})
df["timestamp"] = pd.to_datetime(df["timestamp"], format="mixed")
df["class"] = df["class"].astype(int)
df["polarisation"] = df["polarisation"].astype(str).str.upper()

print(f"Loaded {len(df)} rows, {df['GRID CELL'].nunique()} tiles, "
      f"{df.groupby(['GRID CELL', 'row', 'column']).ngroups} grid cells")
print(f"Classes present: {sorted(df['class'].unique().tolist())}")


df_vv = df[df["polarisation"] == "VV"].copy()
df_vh = df[df["polarisation"] == "VH"].copy()

# Drop UNDEFINED rows from feature analysis (they carry no label signal)
df_vv_labelled = df_vv[df_vv["class"].isin(PLOTTABLE_CLASSES)].copy()
df_vh_labelled = df_vh[df_vh["class"].isin(PLOTTABLE_CLASSES)].copy()

print(f"Labelled VV cells: {len(df_vv_labelled)}")
print(f"Labelled VH cells: {len(df_vh_labelled)}")

n_feats = len(FEATURES)
n_cols  = 3
n_rows  = int(np.ceil(n_feats / n_cols))
fig, axes = plt.subplots(n_rows, n_cols, figsize=(16, 5 * n_rows))
axes = axes.flatten()

for i, feat in enumerate(FEATURES):
    ax = axes[i]
    csv_col = [k for k, v in CSV_TO_FEATURE.items() if v is feat][0]
    for cls_id in PLOTTABLE_CLASSES:
        subset = df_vv_labelled[df_vv_labelled["class"] == cls_id][csv_col].dropna()
        if len(subset) == 0:
            continue
        ax.hist(
            subset, bins=30, alpha=0.55,
            color=CLASS_COLOURS[cls_id],
            label=f"{cls_id}: {CLASS_LABELS[cls_id]} (n={len(subset)})",
            edgecolor="white", linewidth=0.5,
        )
    ax.set_xlabel(f"{feat.nameStr}", fontsize=10)
    ax.set_ylabel("Frequency", fontsize=10)
    ax.set_title(feat.nameStr, fontsize=12, fontweight="bold")
    ax.grid(alpha=0.3, linestyle="--")

for j in range(n_feats, len(axes)):
    axes[j].axis("off")
legend_ax = axes[n_feats] if n_feats < len(axes) else axes[-1]
handles = [
    Patch(facecolor=CLASS_COLOURS[c], edgecolor="gray",
          label=f"{c}: {CLASS_LABELS[c]}")
    for c in PLOTTABLE_CLASSES
]
legend_ax.legend(handles=handles, loc="center", fontsize=10,
                 frameon=True, title="Class", title_fontsize=11)

plt.suptitle("Distribution of SAR Features by Land Class (VV)",
             fontsize=14, fontweight="bold")
plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/01_feature_histograms_{datetime.now()}.png", dpi=150, bbox_inches="tight")
plt.close()
print("Saved 01_feature_histograms.png")


fig, axes = plt.subplots(1, n_feats, figsize=(4 * n_feats, 4.5))

for ax, feat in zip(axes, FEATURES):
    csv_col = [k for k, v in CSV_TO_FEATURE.items() if v is feat][0]
    vv = df_vv_labelled[csv_col].dropna()
    vh = df_vh_labelled[csv_col].dropna()

    identical = (
        len(vv) > 0 and len(vh) > 0
        and np.allclose(vv.values[:min(len(vv), len(vh))],
                        vh.values[:min(len(vv), len(vh))],
                        rtol=1e-6)
    )

    if identical:
        ax.hist(vv, bins=30, alpha=0.7, color=POLARISATION_COLOURS["VV"],
                edgecolor="white", linewidth=0.5)
        ax.set_title(f"{feat.nameStr}\n(VV only)", fontsize=10)
    else:
        ax.hist(vv, bins=30, alpha=0.55, color=POLARISATION_COLOURS["VV"],
                label="VV", edgecolor="white", linewidth=0.5)
        ax.hist(vh, bins=30, alpha=0.55, color=POLARISATION_COLOURS["VH"],
                label="VH", edgecolor="white", linewidth=0.5)
        ax.legend(fontsize=9)
        ax.set_title(feat.nameStr, fontsize=11, fontweight="bold")

    ax.set_xlabel(feat.nameStr, fontsize=9)
    ax.set_ylabel("Frequency", fontsize=9)
    ax.grid(alpha=0.3, linestyle="--")

plt.suptitle("VV vs VH Polarisation Comparison",
             fontsize=14, fontweight="bold")
plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/02_polarisation_comparison_{datetime.now()}.png", dpi=150, bbox_inches="tight")
plt.close()
print("Saved 02_polarisation_comparison.png")

feat_cols = list(CSV_TO_FEATURE.keys())
n = len(feat_cols)

fig, axes = plt.subplots(n, n, figsize=(14, 14))

for i, fi in enumerate(feat_cols):
    for j, fj in enumerate(feat_cols):
        ax = axes[i, j]
        if i == j:
            for cls_id in PLOTTABLE_CLASSES:
                subset = df_vv_labelled[df_vv_labelled["class"] == cls_id][fi].dropna()
                if len(subset) > 0:
                    ax.hist(subset, bins=20, alpha=0.6,
                            color=CLASS_COLOURS[cls_id], edgecolor="none")
            ax.set_ylabel("Freq", fontsize=7)
        else:
            for cls_id in PLOTTABLE_CLASSES:
                subset = df_vv_labelled[df_vv_labelled["class"] == cls_id]
                ax.scatter(subset[fj], subset[fi],
                           s=8, alpha=0.5, c=CLASS_COLOURS[cls_id],
                           edgecolors="none")
        if i == n - 1:
            ax.set_xlabel(CSV_TO_FEATURE[fj].nameStr, fontsize=8)
        if j == 0:
            ax.set_ylabel(CSV_TO_FEATURE[fi].nameStr, fontsize=8)
        ax.tick_params(labelsize=6)
        ax.grid(alpha=0.2, linestyle="--")

handles = [
    Line2D([0], [0], marker="o", color="w",
           markerfacecolor=CLASS_COLOURS[c], markersize=8,
           label=f"{c}: {CLASS_LABELS[c]}")
    for c in PLOTTABLE_CLASSES
]
fig.legend(handles=handles, loc="upper right", fontsize=10,
           frameon=True, title="Class")
plt.suptitle("Pairwise Feature Scatter Matrix (VV)",
             fontsize=14, fontweight="bold")
plt.tight_layout(rect=[0, 0, 0.92, 1])
plt.savefig(f"{OUTPUT_DIR}/03_feature_scatter_matrix_{datetime.now()}.png", dpi=150, bbox_inches="tight")
plt.close()
print("Saved 03_feature_scatter_matrix.png")

fig, axes = plt.subplots(1, 2, figsize=(14, 7))

# --- Left: class map ---
ax = axes[0]
for cls_id in PLOTTABLE_CLASSES:
    subset = df_vv_labelled[df_vv_labelled["class"] == cls_id]
    if len(subset) == 0:
        continue
    ax.scatter(
        subset["x"], subset["y"],
        s=25, c=CLASS_COLOURS[cls_id],
        label=f"{cls_id}: {CLASS_LABELS[cls_id]}",
        edgecolors="black", linewidths=0.3, alpha=0.85,
    )
ax.set_xlabel("X (Lo19, metres)", fontsize=10)
ax.set_ylabel("Y (Lo19, metres)", fontsize=10)
ax.set_title("Spatial Distribution of Sampled Cells", fontsize=12, fontweight="bold")
ax.legend(fontsize=9, loc="best")
ax.grid(alpha=0.3, linestyle="--")
ax.set_aspect("equal", adjustable="box")

# --- Right: log intensity as continuous colour ---
ax = axes[1]
sc = ax.scatter(
    df_vv_labelled["x"], df_vv_labelled["y"],
    c=df_vv_labelled["log_intensity"],
    cmap=Feature.LOG_INTENSITY.colourMap,
    s=25, edgecolors="black", linewidths=0.2,
)
plt.colorbar(sc, ax=ax, label=Feature.LOG_INTENSITY.nameStr)
ax.set_xlabel("X (Lo19, metres)", fontsize=10)
ax.set_ylabel("Y (Lo19, metres)", fontsize=10)
ax.set_title("Log Intensity Across Space", fontsize=12, fontweight="bold")
ax.grid(alpha=0.3, linestyle="--")
ax.set_aspect("equal", adjustable="box")

plt.suptitle("Spatial View of Sampled Grid Cells (VV)",
             fontsize=14, fontweight="bold")
plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/04_spatial_class_map_{datetime.now()}.png", dpi=150, bbox_inches="tight")
plt.close()
print("Saved 04_spatial_class_map.png")


fig, axes = plt.subplots(1, n_feats, figsize=(4 * n_feats, 5))

for ax, feat in zip(axes, FEATURES):
    csv_col = [k for k, v in CSV_TO_FEATURE.items() if v is feat][0]
    data, positions, colours = [], [], []
    for cls_id in PLOTTABLE_CLASSES:
        subset = df_vv_labelled[df_vv_labelled["class"] == cls_id][csv_col].dropna()
        if len(subset) > 0:
            data.append(subset.values)
            positions.append(cls_id)
            colours.append(CLASS_COLOURS[cls_id])

    if not data:
        ax.axis("off")
        continue

    bp = ax.boxplot(
        data, positions=positions, widths=0.6,
        patch_artist=True, showfliers=True,
        flierprops=dict(marker="o", markersize=3, alpha=0.5),
    )
    for patch, colour in zip(bp["boxes"], colours):
        patch.set_facecolor(colour)
        patch.set_alpha(0.7)
    ax.set_xticks(positions)
    ax.set_xticklabels([CLASS_LABELS[p] for p in positions],
                       rotation=45, ha="right", fontsize=8)
    ax.set_ylabel(feat.nameStr, fontsize=9)
    ax.set_title(feat.nameStr, fontsize=11, fontweight="bold")
    ax.grid(alpha=0.3, linestyle="--", axis="y")

plt.suptitle("Feature Distributions by Land Class (VV)",
             fontsize=14, fontweight="bold")
plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/05_boxplots_by_class_{datetime.now()}.png", dpi=150, bbox_inches="tight")
plt.close()
print("Saved 05_boxplots_by_class.png")

corr = df_vv_labelled[feat_cols].corr()

fig, ax = plt.subplots(figsize=(8, 6.5))
im = ax.imshow(corr, cmap="RdBu_r", vmin=-1, vmax=1, aspect="auto")

for i in range(len(feat_cols)):
    for j in range(len(feat_cols)):
        val = corr.iloc[i, j]
        ax.text(j, i, f"{val:.2f}", ha="center", va="center",
                color="white" if abs(val) > 0.5 else "black",
                fontsize=10, fontweight="bold")

ax.set_xticks(range(len(feat_cols)))
ax.set_yticks(range(len(feat_cols)))
ax.set_xticklabels([CSV_TO_FEATURE[f].nameStr for f in feat_cols],
                   rotation=45, ha="right", fontsize=9)
ax.set_yticklabels([CSV_TO_FEATURE[f].nameStr for f in feat_cols], fontsize=9)
plt.colorbar(im, ax=ax, label="Pearson correlation")
ax.set_title("Feature Correlation Matrix (VV)",
             fontsize=12, fontweight="bold")
plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/06_correlation_heatmap_{datetime.now()}.png", dpi=150, bbox_inches="tight")
plt.close()
print("Saved 06_correlation_heatmap.png")


fig, axes = plt.subplots(1, 2, figsize=(12, 5))

ax = axes[0]
counts = df_vv_labelled["class"].value_counts().sort_index()
bars = ax.bar(
    [f"{c}: {CLASS_LABELS[c]}" for c in counts.index],
    counts.values,
    color=[CLASS_COLOURS[c] for c in counts.index],
    edgecolor="black", linewidth=0.5,
)
for bar, v in zip(bars, counts.values):
    ax.text(bar.get_x() + bar.get_width() / 2, v + 1, str(v),
            ha="center", va="bottom", fontsize=9, fontweight="bold")
ax.set_ylabel("Number of cells", fontsize=10)
ax.set_title("Class Balance (VV)", fontsize=12, fontweight="bold")
ax.tick_params(axis="x", rotation=45, labelsize=8)
ax.grid(alpha=0.3, linestyle="--", axis="y")

ax = axes[1]
tile_class = (df_vv_labelled
              .groupby(["GRID CELL", "class"])
              .size()
              .unstack(fill_value=0))
bottom = np.zeros(len(tile_class))
for cls_id in PLOTTABLE_CLASSES:
    if cls_id not in tile_class.columns:
        continue
    ax.bar(
        tile_class.index, tile_class[cls_id].values,
        bottom=bottom, color=CLASS_COLOURS[cls_id],
        label=f"{cls_id}: {CLASS_LABELS[cls_id]}",
        edgecolor="white", linewidth=0.5,
    )
    bottom += tile_class[cls_id].values
ax.set_ylabel("Number of cells", fontsize=10)
ax.set_title("Class Composition per Tile", fontsize=12, fontweight="bold")
ax.tick_params(axis="x", rotation=45, labelsize=8)
ax.legend(fontsize=8, loc="upper right")
ax.grid(alpha=0.3, linestyle="--", axis="y")

plt.suptitle("Class Balance and Tile Composition",
             fontsize=14, fontweight="bold")
plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/07_class_balance_{datetime.now()}.png", dpi=150, bbox_inches="tight")
plt.close()
print("Saved 07_class_balance.png")

print("\nAll plots generated successfully.")