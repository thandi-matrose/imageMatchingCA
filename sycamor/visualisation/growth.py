import os
import json
import ast
from datetime import datetime
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import matplotlib.ticker as mtick
from sycamor.ca.classification.scheme import LandClass
from sycamor.visualisation.plot import addStyle

# Mocking LandClass for the script to run independently

CLASS_COLOURS = {c.index: c.colour for c in list(LandClass)}
CLASS_LABELS  = {c.index: c.displayName for c in list(LandClass)}
PLOTTABLE_CLASSES = [c.index for c in list(LandClass) if c.index != 0]

# ---------------------------------------------------------------------------
# Configuration & Paths
# ---------------------------------------------------------------------------
SUMMARY_CSV = "results/experiments/run2/run_summary.csv"      # Replace with your actual summary file path
TIMESTEPS_CSV = "results/experiments/run2/run_timesteps.csv"  # Replace with your actual timesteps file path
OUTPUT_DIR = "results/experiments/run2/plots"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ---------------------------------------------------------------------------
# Helper Functions
# ---------------------------------------------------------------------------
def parse_json_column(val):
    """Safely parse stringified JSON dictionaries from pandas."""
    if pd.isna(val) or val == "":
        return {}
    try:
        # Handles the double-quote escaping seen in your CSV snippet
        return json.loads(val.replace('""', '"'))
    except json.JSONDecodeError:
        try:
            return ast.literal_eval(val)
        except:
            return {}

def load_data():
    """Load and preprocess both CSVs."""
    print("Loading data...")
    
    # 1. Load Summary
    df_summary = pd.read_csv(SUMMARY_CSV)
    df_summary["class_counts_final"] = df_summary["class_counts_final"].apply(parse_json_column)
    df_summary["class_counts_new_totals"] = df_summary["class_counts_new_totals"].apply(parse_json_column)
    
    # 2. Load Timesteps
    df_steps = pd.read_csv(TIMESTEPS_CSV)
    df_steps["new_per_class"] = df_steps["new_per_class"].apply(parse_json_column)
    df_steps["class_counts_after_step"] = df_steps["class_counts_after_step"].apply(parse_json_column)
    
    # Ensure generation is numeric
    df_steps["generation"] = pd.to_numeric(df_steps["generation"])
    
    return df_summary, df_steps

# ---------------------------------------------------------------------------
# Plotting Functions
# ---------------------------------------------------------------------------
def plot_convergence(df_steps):
    """Plot the number of cells classified per generation for each tile."""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    for grid_cell, group in df_steps.groupby("gridCell"):
        # Smooth the curve slightly to make it readable (optional)
        # y_smooth = group["cells_classified_this_step"].rolling(window=5, min_periods=1).mean()
        ax.plot(
            group["generation"], 
            group["cells_classified_this_step"], 
            label=grid_cell, 
            linewidth=2,
            alpha=0.8
        )

    ax.set_xlabel("Generation", fontsize=12)
    ax.set_ylabel("Cells Classified This Step", fontsize=12)
    ax.set_title("Convergence Rate per Generation", fontsize=14, fontweight="bold")
    ax.grid(alpha=0.3, linestyle="--")
    
    # Cap x-axis at 200 to see the initial spike clearly, unless it's too short
    max_gen = df_steps["generation"].max()
    if max_gen > 200:
        ax.set_xlim(0, 200)
        ax.text(0.5, 0.9, "Note: X-axis capped at 200 generations for clarity.", 
                transform=ax.transAxes, ha="center", color="gray", fontsize=10)

    ax.legend(loc="upper right", title="Grid Cell", frameon=True)
    plt.tight_layout()
    path = f"{OUTPUT_DIR}/01_convergence_rate_{datetime.now().strftime('%H%M%S')}.png"
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved {path}")

def plot_remaining_unclassified(df_steps):
    """Plot the cumulative remaining unclassified cells over time."""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    for grid_cell, group in df_steps.groupby("gridCell"):
        ax.plot(
            group["generation"], 
            group["remaining_unclassified"], 
            label=grid_cell, 
            linewidth=2
        )

    ax.set_xlabel("Generation", fontsize=12)
    ax.set_ylabel("Remaining Unclassified Cells", fontsize=12)
    ax.set_title("Convergence to Full Classification", fontsize=14, fontweight="bold")
    ax.grid(alpha=0.3, linestyle="--")
    ax.legend(loc="upper right", title="Grid Cell")
    
    # Use log scale if the drop is very rapid
    ax.set_yscale('log')
    ax.set_ylabel("Remaining Unclassified Cells (Log Scale)", fontsize=12)
    
    plt.tight_layout()
    path = f"{OUTPUT_DIR}/02_remaining_unclassified_{datetime.now().strftime('%H%M%S')}.png"
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved {path}")

def plot_alpha_schedule(df_steps):
    """Plot the alpha(t) ramping over time."""
    fig, ax = plt.subplots(figsize=(8, 4))
    
    # Just plot the first tile, as alpha should be identical across all tiles
    first_cell = df_steps["gridCell"].iloc[0]
    group = df_steps[df_steps["gridCell"] == first_cell]
    
    ax.plot(group["generation"], group["alpha_t"], color="#914545", linewidth=2.5)
    
    ax.set_xlabel("Generation", fontsize=12)
    ax.set_ylabel(r"\(\alpha(t)\) Weight", fontsize=12)
    ax.set_title(f"Alpha Schedule (Time to Terminal Velocity) - {first_cell}", fontsize=12, fontweight="bold")
    ax.grid(alpha=0.3, linestyle="--")
    ax.set_ylim(0, 1.05)
    
    plt.tight_layout()
    path = f"{OUTPUT_DIR}/03_alpha_schedule_{datetime.now().strftime('%H%M%S')}.png"
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved {path}")

def plot_step_time(df_steps):
    """Plot the computational time per generation."""
    fig, ax = plt.subplots(figsize=(10, 5))
    
    # Average step time across all tiles to see the general trend
    avg_time = df_steps.groupby("generation")["step_time_s"].mean()
    
    ax.plot(avg_time.index, avg_time.values, color="#4A90D9", linewidth=2)
    ax.fill_between(avg_time.index, avg_time.values, alpha=0.2, color="#4A90D9")
    
    ax.set_xlabel("Generation", fontsize=12)
    ax.set_ylabel("Average Step Time (seconds)", fontsize=12)
    ax.set_title("Computational Cost per Generation", fontsize=14, fontweight="bold")
    ax.grid(alpha=0.3, linestyle="--")
    
    plt.tight_layout()
    path = f"{OUTPUT_DIR}/04_step_time_{datetime.now().strftime('%H%M%S')}.png"
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved {path}")

def plot_class_growth(df_steps, target_cell=None):
    """Plot the cumulative class counts over time for a specific tile."""
    if target_cell is None:
        target_cell = df_steps["gridCell"].iloc[0]
        
    group = df_steps[df_steps["gridCell"] == target_cell].copy()
    
    # Explode the class_counts_after_step dictionary into columns
    counts_df = group["class_counts_after_step"].apply(pd.Series).fillna(0)
    counts_df["generation"] = group["generation"].values
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    for cls_id in PLOTTABLE_CLASSES:
        if str(cls_id) in counts_df.columns:
            ax.plot(
                counts_df["generation"], 
                counts_df[str(cls_id)], 
                label=CLASS_LABELS[cls_id], 
                color=CLASS_COLOURS[cls_id], 
                linewidth=2
            )
            
    ax.set_xlabel("Generation", fontsize=12)
    ax.set_ylabel("Cumulative Classified Cells", fontsize=12)
    ax.set_title(f"Class Growth Over Time - {target_cell}", fontsize=14, fontweight="bold")
    ax.grid(alpha=0.3, linestyle="--")
    ax.legend(loc="upper right", title="Land Class", frameon=True)
    
    plt.tight_layout()
    path = f"{OUTPUT_DIR}/05_class_growth_{target_cell}_{datetime.now().strftime('%H%M%S')}.png"
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved {path}")

def plot_summary_comparison(df_summary):
    """Bar chart comparing initial vs final classified cells per tile."""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    cells = df_summary["gridCell"]
    x = np.arange(len(cells))
    width = 0.25
    
    ax.bar(x - width, df_summary["initial_classified"], width, label="Initial (Seeded)", color="#8da0cb")
    ax.bar(x, df_summary["final_classified"], width, label="Final (Classified)", color="#66c2a5")
    ax.bar(x + width, df_summary["final_unclassified"], width, label="Remaining (Unclassified)", color="#fc8d62")
    
    ax.set_ylabel("Number of Cells", fontsize=12)
    ax.set_title("Seeding vs Final Classification Performance", fontsize=14, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(cells, rotation=45, ha="right")
    ax.grid(alpha=0.3, linestyle="--", axis="y")
    ax.legend()
    
    plt.tight_layout()
    path = f"{OUTPUT_DIR}/06_summary_comparison_{datetime.now().strftime('%H%M%S')}.png"
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved {path}")

def plot_efficiency(df_summary):
    """Plot the speed of classification per tile."""
    fig, ax1 = plt.subplots(figsize=(10, 6))
    
    cells = df_summary["gridCell"]
    x = np.arange(len(cells))
    
    # Bar chart for speed
    bars = ax1.bar(x, df_summary["avg_cells_classified_per_second"], color="#914545", alpha=0.7)
    ax1.set_ylabel("Avg Cells Classified / Sec", fontsize=12, color="#914545")
    ax1.tick_params(axis='y', labelcolor="#914545")
    
    # Line chart for generations run
    ax2 = ax1.twinx()
    ax2.plot(x, df_summary["generations_run"], color="#000000", marker="o", linewidth=2, label="Generations")
    ax2.set_ylabel("Generations to Converge", fontsize=12, color="#000000")
    ax2.tick_params(axis='y', labelcolor="#000000")
    
    ax1.set_xticks(x)
    ax1.set_xticklabels(cells, rotation=45, ha="right")
    ax1.set_title("Algorithmic Efficiency per Tile", fontsize=14, fontweight="bold")
    
    plt.tight_layout()
    path = f"{OUTPUT_DIR}/07_efficiency_{datetime.now().strftime('%H%M%S')}.png"
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved {path}")

# ---------------------------------------------------------------------------
# Main Execution
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    addStyle()
    try:
        df_summary, df_steps = load_data()
        
        print("\nGenerating plots...")
        plot_convergence(df_steps)
        plot_remaining_unclassified(df_steps)
        plot_alpha_schedule(df_steps)
        plot_step_time(df_steps)
        plot_class_growth(df_steps) # You can pass a specific gridCell string here
        plot_summary_comparison(df_summary)
        plot_efficiency(df_summary)
        
        print("\nAll plots generated successfully.")
        
    except FileNotFoundError as e:
        print(f"\nError: Could not find the CSV files. Please ensure SUMMARY_CSV and TIMESTEPS_CSV are correct. \nDetails: {e}")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")