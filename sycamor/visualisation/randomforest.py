import os
from matplotlib import colors
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import rasterio
import seaborn as sns
from datetime import datetime

from sycamor.ca.classification.scheme import LandClass
from sycamor.config.syCAMOR import WOODSTOCK_BOXES
from sycamor.visualisation.plot import addStyle

# ---------------------------------------------------------------------------
# Configuration & Styling
# ---------------------------------------------------------------------------
CSV_PATH = "results/randomforest/run2/prediction_results.csv"  # Replace with your actual file path
OUTPUT_DIR = "results/randomforest/run2"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Class mapping based on your previous syCAMOR scheme
CLASS_LABELS = dict(enumerate(LandClass.getNames()))

CLASS_COLOURS = dict(enumerate(LandClass.getColours()))

# ---------------------------------------------------------------------------
# 1. Load and Prepare Data
# ---------------------------------------------------------------------------
def load_data():
    df = pd.read_csv(CSV_PATH)
    df  = df[df["tile_id"].isin(WOODSTOCK_BOXES)]
    # Ensure numeric types (in case of any weird CSV parsing)
    for c in df.columns:
        if c.startswith("class_"):
            df[c] = pd.to_numeric(df[c], errors='coerce')
            
    # Add a helper column for MB processed per second to evaluate efficiency
    # (Assuming 1 pixel = 3 bands * 1 byte = 3 bytes, so 16M pixels is ~48MB)
    df["megapixels"] = df["total_pixels"] / 1_000_000
    df["mp_per_second"] = df["megapixels"] / df["elapsed_seconds"]
    
    return df

# ---------------------------------------------------------------------------
# 2. Generate 10 DataFrames
# ---------------------------------------------------------------------------
def generate_dataframes(df):
    print("\n--- Generating DataFrames ---")
    
    # DF1: Raw Data (sorted by tile ID)
    df1_raw = df.sort_values("tile_id").reset_index(drop=True)
    print(f"DF1: Raw Data ({len(df1_raw)} rows)")

    # DF2: Melted (Long format) - essential for plotting
    pct_cols = [f"class_{i}_pct" for i in range(1, 8)]
    df2_melted = pd.melt(
        df, 
        id_vars=["tile_id"], 
        value_vars=pct_cols, 
        var_name="Class_Col", 
        value_name="Percentage"
    )
    df2_melted["Class_ID"] = df2_melted["Class_Col"].str.extract(r'class_(\d+)_pct').astype(int)
    df2_melted["Class_Name"] = df2_melted["Class_ID"].map(CLASS_LABELS)
    print("DF2: Melted Data (Long format)")

    # DF3: Class Totals (Study Area level)
    px_cols = [f"class_{i}_px" for i in range(1, 8)]
    df3_totals = pd.DataFrame({
        "Class_ID": range(1, 8),
        "Total_Pixels": [df[c].sum() for c in px_cols]
    })
    df3_totals["Class_Name"] = df3_totals["Class_ID"].map(CLASS_LABELS)
    df3_totals["Pct_of_Study_Area"] = (df3_totals["Total_Pixels"] / df["total_pixels"].sum()) * 100
    print("DF3: Total Pixels per Class")

    # DF4: Dominant Class per Tile
    # We find the column with the max percentage for each row
    df4_dominant = df[["tile_id"]].copy()
    df4_dominant["Dominant_Class_ID"] = df[pct_cols].idxmax(axis=1).str.extract(r'(\d+)').astype(int)
    df4_dominant["Dominant_Class_Name"] = df4_dominant["Dominant_Class_ID"].map(CLASS_LABELS)
    df4_dominant["Dominant_Pct"] = df[pct_cols].max(axis=1)
    print("DF4: Dominant Class per Tile")

    # DF5: Summary Statistics per Class (Mean, Std, Min, Max)
    df5_summary = df2_melted.groupby("Class_Name")["Percentage"].agg(
        ["mean", "std", "min", "max", "median"]
    ).round(2).reset_index()
    print("DF5: Summary Statistics of Class Percentages")

    # DF6: Processing Efficiency
    df6_efficiency = df[["tile_id", "elapsed_seconds", "mp_per_second"]].copy()
    df6_efficiency = df6_efficiency.sort_values("mp_per_second", ascending=False)
    print("DF6: Processing Efficiency")

    # DF7: Correlation Matrix (Do certain classes co-occur?)
    df7_corr = df[pct_cols].corr().round(2)
    df7_corr.columns = [CLASS_LABELS[i] for i in range(1, 8)]
    df7_corr.index = [CLASS_LABELS[i] for i in range(1, 8)]
    print("DF7: Correlation Matrix of Class Percentages")

    # DF8: Top 3 Classes per Tile
    df8_top3 = []
    for _, row in df.iterrows():
        # Sort the percentages and get top 3
        sorted_classes = row[pct_cols].astype(float).sort_values(ascending=False)
        top3 = sorted_classes.head(3)
        for rank, (col, val) in enumerate(top3.items(), 1):
            cls_id = int(col.split('_')[1])
            df8_top3.append({
                "tile_id": row["tile_id"],
                "Rank": rank,
                "Class": CLASS_LABELS[cls_id],
                "Percentage": val
            })
    df8_top3 = pd.DataFrame(df8_top3)
    print("DF8: Top 3 Classes per Tile")

    # DF9: Cumulative Percentage (How much of the tile is covered by the top N classes?)
    df9_cumulative = []
    for _, row in df.iterrows():
        sorted_pcts = row[pct_cols].astype(float).sort_values(ascending=False)
        cum_pct = sorted_pcts.cumsum()
        df9_cumulative.append({
            "tile_id": row["tile_id"],
            "Top_1_Coverage": cum_pct.iloc[0],
            "Top_2_Coverage": cum_pct.iloc[1],
            "Top_3_Coverage": cum_pct.iloc[2],
        })
    df9_cumulative = pd.DataFrame(df9_cumulative)
    print("DF9: Cumulative Coverage of Top N Classes")

    # DF10: Class Balance Deviation (How far is each tile from the global average?)
    global_pct = df3_totals.set_index("Class_ID")["Pct_of_Study_Area"]
    df10_deviation = df[["tile_id"]].copy()
    for i in range(1, 8):
        df10_deviation[f"Class_{i}_Dev"] = df[f"class_{i}_pct"] - global_pct[i]
    print("DF10: Class Deviation from Global Average")

    return {
        "df1_raw": df1_raw, "df2_melted": df2_melted, "df3_totals": df3_totals,
        "df4_dominant": df4_dominant, "df5_summary": df5_summary, "df6_efficiency": df6_efficiency,
        "df7_corr": df7_corr, "df8_top3": df8_top3, "df9_cumulative": df9_cumulative,
        "df10_deviation": df10_deviation
    }

# ---------------------------------------------------------------------------
# 3. Generate 10 Plots
# ---------------------------------------------------------------------------
def generate_plots(df, dfs):
    print("\n--- Generating Plots ---")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Helper to save plots
    def save_plot(fig, name):
        path = f"{OUTPUT_DIR}/{name}_{timestamp}.png"
        fig.savefig(path, dpi=150, bbox_inches="tight")
        plt.close(fig)
        print(f"Saved {path}")

    # Plot 1: Stacked Bar Chart (Class Percentage per Tile)
    fig, ax = plt.subplots(figsize=(12, 6))
    # 1. Create the legend and store it in a variable
    legend = ax.legend()

    # 2. Get the frame object and change its border thickness
    legend.get_frame().set_linewidth(1)

    # Optional: Change the border color too
    legend.get_frame().set_edgecolor("black")
    pivot_pct = df.set_index("tile_id")[[f"class_{i}_pct" for i in range(1, 8)]]
    pivot_pct.columns = [CLASS_LABELS[i] for i in range(1, 8)]
    
    pivot_pct.plot(kind="bar", stacked=True, ax=ax, color=[CLASS_COLOURS[i] for i in range(1, 8)], edgecolor="black", linewidth=0.5)
    ax.set_ylabel("Percentage of Tile (\%)")
    ax.set_xlabel("Grid Cell")
    ax.set_title("Class Composition per Tile (Stacked)", fontweight="bold")
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha="right")
    ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', title="Land Class")
    plt.tight_layout()
    save_plot(fig, "01_stacked_composition")

    # Plot 2: Boxplot of Class Percentages
    fig, ax = plt.subplots(figsize=(10, 6))
    pal = list(CLASS_COLOURS.values())
    pal.remove("#ffffff")
    sns.boxplot(data=dfs["df2_melted"], x="Class_Name", y="Percentage", palette=pal, ax=ax)
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha="right")
    ax.set_title("Distribution of Class Percentages Across All Tiles", fontweight="bold")
    ax.set_xlabel("")
    ax.set_ylabel("Tile Coverage (\%)")
    plt.tight_layout()
    save_plot(fig, "02_class_distribution_boxplot")

    # Plot 3: Pie Chart of Total Study Area
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.pie(dfs["df3_totals"]["Total_Pixels"], labels=dfs["df3_totals"]["Class_Name"], 
           colors=[CLASS_COLOURS[i] for i in range(1, 8)], autopct='%1.1f%%',
           startangle=140, wedgeprops={'edgecolor': 'black', 'linewidth': 0.5})
    ax.set_title("Total Study Area Composition (Random Forest)", fontweight="bold")
    plt.tight_layout()
    save_plot(fig, "03_total_study_area_pie")

    # Plot 4: Dominant Class Count (How many tiles are dominated by which class?)
    fig, ax = plt.subplots(figsize=(10, 5))
    dominant_counts = dfs["df4_dominant"]["Dominant_Class_Name"].value_counts()
    sns.barplot(x=dominant_counts.index, y=dominant_counts.values, 
                palette=[CLASS_COLOURS[list(CLASS_LABELS.values()).index(x)+1] for x in dominant_counts.index], ax=ax)
    ax.set_title("Number of Tiles Dominated by Each Class", fontweight="bold")
    ax.set_ylabel("Number of Tiles")
    ax.set_xlabel("")
    ax.tick_params(axis='x', rotation=45)
    plt.tight_layout()
    save_plot(fig, "04_dominant_class_counts")

    # Plot 5: Processing Time per Tile
    fig, ax = plt.subplots(figsize=(12, 5))
    sns.barplot(data=dfs["df6_efficiency"], x="tile_id", y="elapsed_seconds", color="#4A90D9", ax=ax)
    ax.set_title("Processing Time per Tile", fontweight="bold")
    ax.set_ylabel("Elapsed Seconds")
    ax.set_xlabel("")
    ax.tick_params(axis='x', rotation=45)
    plt.tight_layout()
    save_plot(fig, "05_processing_time")

    # Plot 6: Heatmap of Class Correlations
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.heatmap(dfs["df7_corr"], annot=True, cmap="RdBu_r", vmin=-1, vmax=1, fmt=".2f", 
                linewidths=.5, ax=ax)
    ax.set_title("Correlation of Class Percentages (Tile Co-occurrence)", fontweight="bold")
    plt.tight_layout()
    save_plot(fig, "06_class_correlation_heatmap")

    # Plot 7: Violin Plot of Processing Efficiency (MP/s)
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.violinplot(y=dfs["df6_efficiency"]["mp_per_second"], color="#914545", ax=ax, inner="quart")
    ax.set_title("Processing Speed Distribution (Megapixels/second)", fontweight="bold")
    ax.set_ylabel("MP/s")
    plt.tight_layout()
    save_plot(fig, "07_speed_violin")

    # Plot 8: Top 3 Classes Coverage (Line plot)
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.lineplot(data=dfs["df9_cumulative"].set_index("tile_id"), marker="o", ax=ax, linewidth=2.5)
    ax.set_title("Cumulative Coverage of Top N Classes per Tile", fontweight="bold")
    ax.set_ylabel("Cumulative Percentage (\%)")
    ax.set_xlabel("")
    ax.tick_params(axis='x', rotation=45)
    ax.legend(title="Coverage", labels=["Top 1", "Top 1+2", "Top 1+2+3"])
    plt.tight_layout()
    save_plot(fig, "08_cumulative_coverage")

    # Plot 9: Deviation Heatmap (Tile vs Global Average)
    fig, ax = plt.subplots(figsize=(10, 6))
    # Prepare deviation df for heatmap
    dev_heatmap = dfs["df10_deviation"].set_index("tile_id")
    dev_heatmap.columns = [CLASS_LABELS[i] for i in range(1, 8)]
    sns.heatmap(dev_heatmap, cmap="coolwarm", center=0, annot=False, linewidths=.5, ax=ax)
    ax.set_title("Deviation from Global Average Class \% (Red = Overrepresented)", fontweight="bold")
    ax.set_xlabel("")
    ax.set_ylabel("Grid Cell")
    ax.tick_params(axis='x', rotation=45)
    plt.tight_layout()
    save_plot(fig, "09_deviation_heatmap")

    # Plot 10: Horizontal Bar Chart of Total Pixels per Class
    fig, ax = plt.subplots(figsize=(10, 6))
    df3_sorted = dfs["df3_totals"].sort_values("Total_Pixels", ascending=True)
    colors = [CLASS_COLOURS[i] for i in df3_sorted["Class_ID"]]
    ax.barh(df3_sorted["Class_Name"], df3_sorted["Total_Pixels"], color=colors, edgecolor="black")
    
    # Add value labels
    for i, v in enumerate(df3_sorted["Total_Pixels"]):
        ax.text(v + (v * 0.01), i, f"{v:,.0f}", va='center', fontsize=10)
        
    ax.set_title("Total Pixel Count per Class (Entire Study Area)", fontweight="bold")
    ax.set_xlabel("Total Pixels")
    ax.set_ylabel("")
    plt.tight_layout()
    save_plot(fig, "10_total_pixels_barh")


def plotAllRandomForest():
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
        with rasterio.open(f"results/randomforest/run2/{cell}_rf.tif") as src:
            band=src.read(1)
        im = ax.imshow(band, cmap=cmap, norm=norm, interpolation='nearest')
        ax.text(50,250, cell,zorder=5)
   
    '''
    cbar = plt.colorbar(im, ax=plt.gca(), ticks=class_ticks)
    cbar.set_ticklabels(class_labels)
    cbar.set_label('Class', fontsize=12)
    '''
    plt.savefig("results/randomforest/run2/allrf"+"_"+datetime.now().strftime("%Y%m%d_%H%M%S")+".png", dpi=300, bbox_inches='tight')
    
    ax.clear()   
# ---------------------------------------------------------------------------
# Main Execution
# ---------------------------------------------------------------------------
def main():
    addStyle()
    
    try:
        df = load_data()
        dfs = generate_dataframes(df)
        generate_plots(df, dfs)
        print("\nAll DataFrames and Plots generated successfully.")
    except FileNotFoundError:
        print(f"\nError: Could not find {CSV_PATH}. Please check the path.")
    except Exception as e:
        print(f"\nAn error occurred: {e}")
        
if __name__ == "__main__":
    addStyle()
    plotAllRandomForest()