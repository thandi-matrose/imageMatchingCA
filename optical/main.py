import os

import joblib

from optical.randomforest import PREDICT_WINDOW, getTiles, predict_tile
from sycamor.config.syCAMOR import WOODSTOCK_BOXES
OPTICAL_DIR       = "data/optical/tiff"

OUTPUT_DIR        = "results/randomforest"
def main():
    # 1. Load the model from the file
    model = joblib.load('results/randomforest/rf_baseline_model.joblib')

    # 1. See the default configuration and hyperparameters
    print("--- Model Information ---")
    print(model)

    # 2. Check explicitly defined hyperparameters
    print("\n--- Model Parameters ---")
    print(model)

    # 3. Verify target classes (if the model has been fitted)
    if hasattr(model, "classes"):
        print(f"\nTarget Classes: {model.classes_}")
        print(f"Number of Features: {model.n_features_in_}")
        print(f"Number of Trees: {len(model.estimators_)}")
    else:
        print("\nNote: This model has not been trained/fitted yet.")
    clf = model["model"]
    tiles = getTiles(WOODSTOCK_BOXES)
    for tile_id, opt_path, _ in tiles:
        out_path = os.path.join(OUTPUT_DIR, f"{tile_id}_rf.tif")
        print(f"Predicting {tile_id} -> {out_path}")
        predict_tile(clf, opt_path, out_path, PREDICT_WINDOW)

if __name__ == "__main__":
    main()