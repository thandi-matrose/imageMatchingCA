

from __future__ import annotations

from datetime import datetime
import json
import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from scipy import stats as sp_stats
import matplotlib.pyplot as plt

from sycamor.ca.classification.scheme import LandClass, TrapezoidalDefinition
from sycamor.ca.features.set import Feature
from sycamor.config.syCAMOR import SAMPLE_BOXES
from sycamor.visualisation.plot import addStyle, writeTable


addStyle()


new_dir = "/home/thandi/HONOURS/imageMatchingCA/" 
os.chdir(new_dir)
print(f"Changed directory to: {os.getcwd()}")

# ---------------------------------------------------------------------------
# CSV column <-> Feature enum mapping
# ---------------------------------------------------------------------------
FEATURE_TO_CSV: Dict[Feature, str] = {
    Feature.LOG_INTENSITY:      "log_intensity",
    Feature.SPECKLE_DIVERGENCE: "speck_diverge",
    Feature.ENERGY_GLCM:        "glcm_energy",
    Feature.MEAN_GLCM:          "glcm_mean",
    Feature.VARIANCE_GLCM:      "glcm_variance",
}
CSV_TO_FEATURE = {v: k for k, v in FEATURE_TO_CSV.items()}
CV_CAP = 5.0              # cap CV at this value before inverting
USE_GEOMETRIC_MEAN = False  # False -> use min; True -> geometric mean

FEATURE_NAMES = {f: f.nameStr for f in Feature}
FEATURE_UNITS = {
    Feature.LOG_INTENSITY:      "dB",
    Feature.SPECKLE_DIVERGENCE: "sigma/mu",
    Feature.ENERGY_GLCM:        "-",
    Feature.MEAN_GLCM:          "intensity",
    Feature.VARIANCE_GLCM:      "intensity2",
}

PERCENTILES = (1, 5, 10, 25, 50, 75, 90, 95, 99)


TRAPEZOID_METHODS: Dict[str, Any] = {
    "narrow":     (25,   40,  60,  75),   # conservative
    "standard":   (10,  25,  75,  90),   # recommended default
    "wide":       (2.5, 15,  85,  97.5), # generous
    "very_wide":  (0,   10,  90,  100),  # min/max with 10% trim
    "mean_sd":    "mean_sd",             # mu +/- sigma, mu +/- 2*sigma
    "median_iqr": "median_iqr",          # Q1 -/+ 1.5*IQR, Q1, Q3
}



# Minimum samples per class for stable percentile estimates
MIN_SAMPLES_WARN = 30
MIN_SAMPLES_FAIL = 10




# ---------------------------------------------------------------------------
# Main summariser
# ---------------------------------------------------------------------------
class ClassSignatureSummariser:
    

    def __init__(self, csv_path: str, exclude_undefined: bool = True):
        self.csv_path = csv_path
        self.exclude_undefined = exclude_undefined
        self.df: Optional[pd.DataFrame] = None
        self.polarisation: Optional[str] = None

        # Populated by compute_* methods
        self.statistics: Optional[pd.DataFrame] = None
        self.candidates: Optional[pd.DataFrame] = None
        self.overlaps: Optional[pd.DataFrame] = None
        self.separability: Optional[pd.DataFrame] = None
        
        self.feature_weights: Optional[pd.DataFrame] = None
        self.recommended: Dict[str, Dict[Feature, TrapezoidalDefinition]] = {}

    # -----------------------------------------------------------------
    # Loading
    # -----------------------------------------------------------------
    def load(self, polarisation: str = "VV") -> "ClassSignatureSummariser":
        """
        Load and clean the CSV.

        Parameters
        ----------
        polarisation : {"VV", "VH", "both"}
            Which polarisation to retain for signature fitting. GLCM features
            are identical across polarisations in the source data, but
            log_intensity and speck_diverge are not. Default "VV" uses the
            reference backscatter band.
        """
        self.polarisation = polarisation

        df = pd.read_csv(self.csv_path)

        # Rename the unnamed timestamp column
        df = df.rename(columns={df.columns[0]: "timestamp"})
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

        # Enforce types
        df["class"] = df["class"].astype(int)
        df["polarisation"] = df["polarisation"].astype(str).str.upper()

        # Feature columns must be numeric
        for csv_col in FEATURE_TO_CSV.values():
            df[csv_col] = pd.to_numeric(df[csv_col], errors="coerce")

        # Filter polarisation
        if polarisation != "both":
            df = df[df["polarisation"] == polarisation.upper()].copy()

        # Drop UNDEFINED if requested
        if self.exclude_undefined:
            df = df[df["class"] != 0].copy()
            
        #FILTER ONLY DESIRED SAMPLE CELLS
        df = df[df["GRID CELL"].isin( SAMPLE_BOXES)].copy()
        # Drop rows with any missing feature
        feature_cols = list(FEATURE_TO_CSV.values())
        before = len(df)
        df = df.dropna(subset=feature_cols).copy()
        dropped = before - len(df)
        if dropped > 0:
            print(f"Dropped {dropped} rows with missing feature values.")

        self.df = df.reset_index(drop=True)
        print(f"Loaded {len(self.df)} rows, "
              f"{self.df['GRID CELL'].nunique()} tiles, "
              f"{self.df['class'].nunique()} classes, "
              f"polarisation={polarisation}")
        return self

    # -----------------------------------------------------------------
    # Per-class per-feature statistics
    # -----------------------------------------------------------------
    def compute_statistics(self) -> "ClassSignatureSummariser":
        """Compute comprehensive descriptive statistics per class per feature."""
        if self.df is None:
            raise RuntimeError("Call load() first.")

        records = []
        for cls_id, group in self.df.groupby("class"):
            cls_name = self._class_name(cls_id)
            for feat, csv_col in FEATURE_TO_CSV.items():
                values = group[csv_col].dropna().values
                n = len(values)
                if n == 0:
                    continue

                record = {
                    "class_index": cls_id,
                    "class_name": cls_name,
                    "feature": feat.name,
                    "feature_display": feat.nameStr,
                    "n_samples": n,
                    "mean": float(np.mean(values)),
                    "std": float(np.std(values, ddof=1)) if n > 1 else 0.0,
                    "min": float(np.min(values)),
                    "max": float(np.max(values)),
                    "range": float(np.max(values) - np.min(values)),
                    "median": float(np.median(values)),
                    "mad": float(np.median(np.abs(values - np.median(values)))),
                    "cv": float(np.std(values, ddof=1) / np.mean(values))
                          if n > 1 and np.mean(values) != 0 else np.nan,
                    "skewness": float(sp_stats.skew(values)) if n > 2 else np.nan,
                    "kurtosis": float(sp_stats.kurtosis(values)) if n > 3 else np.nan,
                    "iqr": float(np.percentile(values, 75) - np.percentile(values, 25)),
                }
                for p in PERCENTILES:
                    record[f"p{p:02d}"] = float(np.percentile(values, p))

                records.append(record)

        self.statistics = pd.DataFrame(records)
        return self

    def compute_trapezoid_candidates(self) -> "ClassSignatureSummariser":
        """Compute candidate trapezoids under each method, per class per feature."""
        if self.df is None:
            raise RuntimeError("Call load() first.")

        records = []
        for cls_id, group in self.df.groupby("class"):
            cls_name = self._class_name(cls_id)
            for feat, csv_col in FEATURE_TO_CSV.items():
                values = group[csv_col].dropna().values
                n = len(values)
                if n < 2:
                    continue

                for method, spec in TRAPEZOID_METHODS.items():
                    trapezoid = self._compute_trapezoid(values, method, spec, n)
                    if trapezoid is None:
                        continue
                    records.append({
                        "class_index": cls_id,
                        "class_name": cls_name,
                        "feature": feat.name,
                        "method": method,
                        "a": trapezoid.a,
                        "b": trapezoid.b,
                        "c": trapezoid.c,
                        "d": trapezoid.d,
                        "core_width": trapezoid.core_width(),
                        "support_width": trapezoid.support_width(),
                        "n_samples": n,
                    })

        self.candidates = pd.DataFrame(records)
        
        return self

    @staticmethod
    def _compute_trapezoid(values: np.ndarray, method: str, spec: Any,
                           n: int) -> Optional[TrapezoidalDefinition]:
        """Compute a single trapezoid for a given method."""
        if isinstance(spec, tuple):
            pa, pb, pc, pd = spec
            a = float(np.percentile(values, pa))
            b = float(np.percentile(values, pb))
            c = float(np.percentile(values, pc))
            d = float(np.percentile(values, pd))
            return TrapezoidalDefinition(a, b, c, d, method, n)

        if spec == "mean_sd":
            mu = float(np.mean(values))
            sd = float(np.std(values, ddof=1))
            return TrapezoidalDefinition(mu - 2 * sd, mu - sd, mu + sd, mu + 2 * sd,
                                   method, n)

        if spec == "median_iqr":
            q1 = float(np.percentile(values, 25))
            q3 = float(np.percentile(values, 75))
            iqr = q3 - q1
            return TrapezoidalDefinition(q1 - 1.5 * iqr, q1, q3, q3 + 1.5 * iqr,
                                   method, n)

        return None

    # -----------------------------------------------------------------
    # Class overlap analysis
    # -----------------------------------------------------------------
    def compute_overlaps(self, method: str) -> "ClassSignatureSummariser":
        
        if self.candidates is None:
            raise RuntimeError("Call compute_trapezoid_candidates() first.")

        cand = self.candidates[self.candidates["method"] == method]
        records = []
        class_ids = sorted(cand["class_index"].unique().tolist())

        for feat in Feature:
            feat_cand = cand[cand["feature"] == feat.name]
            for i, c1 in enumerate(class_ids):
                for c2 in class_ids[i + 1:]:
                    r1 = feat_cand[feat_cand["class_index"] == c1]
                    r2 = feat_cand[feat_cand["class_index"] == c2]
                    if len(r1) == 0 or len(r2) == 0:
                        continue
                    r1 = r1.iloc[0]
                    r2 = r2.iloc[0]

                    core_int = max(0.0, min(r1["c"], r2["c"]) - max(r1["b"], r2["b"]))
                    supp_int = max(0.0, min(r1["d"], r2["d"]) - max(r1["a"], r2["a"]))
                    min_core = max(min(r1["core_width"], r2["core_width"]), 1e-12)
                    min_supp = max(min(r1["support_width"], r2["support_width"]), 1e-12)

                    records.append({
                        "class_a": c1,
                        "class_b": c2,
                        "class_a_name": self._class_name(c1),
                        "class_b_name": self._class_name(c2),
                        "feature": feat.name,
                        "core_overlap_ratio": core_int / min_core,
                        "support_overlap_ratio": supp_int / min_supp,
                    })

        self.overlaps = pd.DataFrame(records)
        return self

    # -----------------------------------------------------------------
    # Separability (Fisher discriminant ratio)
    # -----------------------------------------------------------------
    def compute_separability(self) -> "ClassSignatureSummariser":  #Fisher's discriminant ratio per class pair per feature
        
        if self.df is None:
            raise RuntimeError("Call load() first.")

        records = []
        class_ids = sorted(self.df["class"].unique().tolist())

        for feat, csv_col in FEATURE_TO_CSV.items():
            for i, c1 in enumerate(class_ids):
                for c2 in class_ids[i + 1:]:
                    v1 = self.df[self.df["class"] == c1][csv_col].dropna().values
                    v2 = self.df[self.df["class"] == c2][csv_col].dropna().values
                    if len(v1) < 2 or len(v2) < 2:
                        continue

                    mu1, mu2 = np.mean(v1), np.mean(v2)
                    s1, s2 = np.var(v1, ddof=1), np.var(v2, ddof=1)
                    denom = s1 + s2
                    f = float((mu1 - mu2) ** 2 / denom) if denom > 0 else np.inf

                    records.append({
                        "class_a": c1, "class_b": c2,
                        "class_a_name": self._class_name(c1),
                        "class_b_name": self._class_name(c2),
                        "feature": feat.nameStr,
                        "fisher_ratio": f,
                    })

        self.separability = pd.DataFrame(records)
        return self
    def compute_feature_weights(
        self,
        combination: str = "min",
        use_fisher: bool = True,
    ) -> pd.DataFrame:
        """
        Compute per-class per-feature weights from separability, consistency,
        and uniqueness scores.

        Parameters
        ----------
        combination : {"min", "geometric_mean"}
            How to combine the three scores. "min" is the fuzzy AND; the
            geometric mean is a softer, more compensatory alternative.
        use_fisher : bool
            If True, use the per-class Fisher ratio for separability. If False,
            use the global eta-squared statistic instead (feature weights are
            then shared across all classes).

        Returns
        -------
        DataFrame with columns:
            class_index, class_name, feature,
            S_sep, S_cons, S_uniq, w_raw, weight
        """
        if self.separability is None:
            raise RuntimeError("Call compute_separability() first.")
        if self.overlaps is None:
            raise RuntimeError("Call compute_overlaps() first.")
        if self.statistics is None:
            raise RuntimeError("Call compute_statistics() first.")
        if not use_fisher and not hasattr(self, "eta_squared"):
            self.compute_eta_squared()

        records = []

        # ---------------------------------------------------------------------
        # 1. Separability score per class per feature
        # ---------------------------------------------------------------------
        if use_fisher:
            # Per-class: aggregate Fisher ratio over all pairs involving class c
            agg_sep = (self.separability
                    .groupby(["class_a_name", "feature"])["fisher_ratio"]
                    .mean()
                    .reset_index())
            # Also aggregate from the class_b side
            agg_sep_b = (self.separability
                        .groupby(["class_b_name", "feature"])["fisher_ratio"]
                        .mean()
                        .reset_index()
                        .rename(columns={"class_b_name": "class_a_name"}))
            agg_sep = pd.concat([agg_sep, agg_sep_b], ignore_index=True)
            agg_sep = (agg_sep.groupby(["class_a_name", "feature"])["fisher_ratio"]
                    .mean()
                    .reset_index())
        else:
            # Global eta-squared shared across classes
            agg_sep = self.eta_squared.rename(columns={"eta_squared": "fisher_ratio"})

        # ---------------------------------------------------------------------
        # 2. Consistency score (from CV within class per feature)
        # ---------------------------------------------------------------------
        stats = self.statistics.copy()
        stats["cv_capped"] = stats["cv"].clip(upper=CV_CAP).fillna(CV_CAP)
        stats["S_cons"] = 1.0 / (1.0 + stats["cv_capped"])

        # ---------------------------------------------------------------------
        # 3. Uniqueness score (from core overlap)
        # ---------------------------------------------------------------------
        ov = self.overlaps.copy()
        ov_a = (ov.groupby(["class_a_name", "feature"])["core_overlap_ratio"]
                .mean().reset_index()
                .rename(columns={"class_a_name": "class_name"}))
        ov_b = (ov.groupby(["class_b_name", "feature"])["core_overlap_ratio"]
                .mean().reset_index()
                .rename(columns={"class_b_name": "class_name"}))
        ov_agg = pd.concat([ov_a, ov_b], ignore_index=True)
        ov_agg = (ov_agg.groupby(["class_name", "feature"])["core_overlap_ratio"]
                .mean().reset_index())
        ov_agg["S_uniq"] = 1.0 - ov_agg["core_overlap_ratio"].clip(0, 1)

        # ---------------------------------------------------------------------
        # 4. Combine per class
        # ---------------------------------------------------------------------
        for cls_id, group in self.df.groupby("class"):
            cls_name = self._class_name(cls_id)

            # Collect scores per feature
            per_feat = {}
            for feat in Feature:
                # Separability
                if use_fisher:
                    row = agg_sep[(agg_sep["class_a_name"] == cls_name)
                                & (agg_sep["feature"] == feat.name)]
                else:
                    row = agg_sep[agg_sep["feature"] == feat.name]
                s_sep = float(row["fisher_ratio"].iloc[0]) if len(row) > 0 else 0.0

                # Consistency
                row = stats[(stats["class_name"] == cls_name)
                            & (stats["feature"] == feat.name)]
                s_cons = float(row["S_cons"].iloc[0]) if len(row) > 0 else 0.0

                # Uniqueness
                row = ov_agg[(ov_agg["class_name"] == cls_name)
                            & (ov_agg["feature"] == feat.name)]
                s_uniq = float(row["S_uniq"].iloc[0]) if len(row) > 0 else 0.0

                per_feat[feat.name] = {
                    "S_sep_raw": s_sep,
                    "S_cons": s_cons,
                    "S_uniq": s_uniq,
                }

            # Normalise S_sep across features within this class
            max_sep = max(v["S_sep_raw"] for v in per_feat.values()) or 1.0
            for fname in per_feat:
                per_feat[fname]["S_sep"] = per_feat[fname]["S_sep_raw"] / max_sep

            # Combine the three scores
            for fname, scores in per_feat.items():
                if combination == "min":
                    w_raw = min(scores["S_sep"], scores["S_cons"], scores["S_uniq"])
                elif combination == "geometric_mean":
                    w_raw = (scores["S_sep"] * scores["S_cons"] * scores["S_uniq"]) ** (1/3)
                else:
                    raise ValueError(f"Unknown combination: {combination}")

                records.append({
                    "class_index": cls_id,
                    "class_name": cls_name,
                    "feature": fname,
                    "S_sep": scores["S_sep"],
                    "S_cons": scores["S_cons"],
                    "S_uniq": scores["S_uniq"],
                    "w_raw": w_raw,
                })

        # Normalise w_raw so weights sum to 1 per class
        weights_df = pd.DataFrame(records)
        weights_df["weight"] = weights_df.groupby("class_name")["w_raw"].transform(
            lambda s: s / s.sum() if s.sum() > 0 else 1.0 / len(s)
        )

        self.feature_weights = weights_df
        return self
    def recommend(self, method: str) -> "ClassSignatureSummariser":
        """
        Build the recommended signature dictionary from a chosen method.

        Result structure:
            {
                "HIGH_DENSITY_URBAN": {
                    Feature.LOG_INTENSITY: TrapezoidalDefinition(...),
                    ...
                },
                ...
            }
        """
        if self.candidates is None:
            raise RuntimeError("Call compute_trapezoid_candidates() first.")

        cand = self.candidates[self.candidates["method"] == method]
        self.recommended = {}

        for cls_id, group in cand.groupby("class_index"):
            cls_name = self._class_name(cls_id)
            sig = {}
            for _, row in group.iterrows():
                feat = Feature[row["feature"]]
                sig[feat] = TrapezoidalDefinition(
                    row["a"], row["b"], row["c"], row["d"],
                    row["method"], int(row["n_samples"])
                )
            self.recommended[cls_name] = sig

        self._recommended_method = method
        return self

    def export_signature(self, path: str) -> None:
        """Export the recommended signature to JSON."""
        if not self.recommended:
            raise RuntimeError("Call recommend() first.")

        payload = {
            "method": self._recommended_method,
            "polarisation": self.polarisation,
            "n_rows": len(self.df) if self.df is not None else 0,
            "signatures": {
                cls_name: {
                    feat.name: {
                        "a": tp.a, "b": tp.b, "c": tp.c, "d": tp.d,
                        "n_samples": tp.n_samples,
                    }
                    for feat, tp in sig.items()
                }
                for cls_name, sig in self.recommended.items()
            },
        }
        with open(path, "w") as f:
            json.dump(payload, f, indent=2)
        print(f"Wrote {path}")

    def export_python_literal(self, path: str) -> None:
        """
        Export a Python literal that can be pasted directly into the
        LandClass enum as the signature argument.
        """
        if not self.recommended:
            raise RuntimeError("Call recommend() first.")

        lines = [
            '"""',
            'Auto-generated by ClassSignatureSummariser.',
            f'Method: {self._recommended_method}',
            f'Polarisation: {self.polarisation}',
            'Paste each block into the corresponding LandClass member.',
            '"""',
            '',
            'from your_module import Feature, TrapezoidalDefinition, BandTrapezoid',
            '',
            'SIGNATURES = {',
        ]
        for cls_name, sig in self.recommended.items():
            lines.append(f'    "{cls_name}": TrapezoidalDefinition(')
            lines.append('        bands={')
            for feat, tp in sig.items():
                lines.append(
                    f'            Feature.{feat.name}: '
                    f'BandTrapezoid({tp.a:.6f}, {tp.b:.6f}, '
                    f'{tp.c:.6f}, {tp.d:.6f}),'
                )
            lines.append('        },')
            lines.append(f'        # n_samples per band: '
                         f'{[tp.n_samples for tp in sig.values()]}')
            lines.append('    ),')
        lines.append('}')
        with open(path, "w") as f:
            f.write("\n".join(lines))
        print(f"Wrote {path}")

    def export_statistics(self, path: str) -> None:
        """Export the full statistics table to CSV."""
        if self.statistics is None:
            raise RuntimeError("Call compute_statistics() first.")
        self.statistics.to_csv(path, index=False)
        df = self.statistics[[ "class_name","feature","n_samples","mean","cv","skewness"]]
        df.rename(columns={'class_name': 'Land Class'}, inplace=True)
        df.rename(columns={'n_samples': '$n$'}, inplace=True)
        df.rename(columns={'cv': 'Coefficient of Variance'}, inplace=True)
        
        df.rename(columns={'mean': 'Mean'}, inplace=True)
        
        df.rename(columns={'skewness': 'Skewness'}, inplace=True)
        for feat in list(Feature):
            subDF = df[df["feature"] == feat.name]
            subDF.drop(columns="feature", inplace=True)
            writeTable(subDF, "feature_stats_"+ feat.name, "Statistics of "+feat.nameStr, False)
        print(f"Wrote {path}")

    def export_candidates(self, path: str) -> None:
        """Export all trapezoid candidates to CSV."""
        if self.candidates is None:
            raise RuntimeError("Call compute_trapezoid_candidates() first.")
        self.candidates.to_csv(path, index=False)
        print(f"Wrote {path}")

    def export_overlaps(self, path: str) -> None:
        if self.overlaps is None:
            raise RuntimeError("Call compute_overlaps() first.")
        self.overlaps.to_csv(path, index=False)
        print(f"Wrote {path}")

    def export_separability(self, path: str) -> None:
        if self.separability is None:
            raise RuntimeError("Call compute_separability() first.")
        self.separability.to_csv(path, index=False)
        df = self.separability[[ "class_a_name","class_b_name","feature","fisher_ratio"]]
        
        df = df.sort_values(by=['feature', 'class_a_name'])

        df.rename(columns={'class_a_name': 'Class A'}, inplace=True)
        df.rename(columns={'class_b_name': 'Class B'}, inplace=True)
        df.rename(columns={'feature': 'Feature'}, inplace=True)
        df.rename(columns={'fisher_ratio': 'Fisher Ratio'}, inplace=True)
        writeTable(df, "separability", "Pairwise Separability of Classes", False)
      
        print(f"Wrote {path}")

    def export_feature_weights(self, path: str) -> None:
        if self.feature_weights is None:
            raise RuntimeError("Call feature_weights() first.")
        self.feature_weights.to_csv(path, index=False)
        print(f"Wrote {path}")
    
    # -----------------------------------------------------------------
    # Plotting
    # -----------------------------------------------------------------
    def plot_all(self, output_dir: str, method:str) -> None:
        """Produce all diagnostic figures."""
        os.makedirs(output_dir, exist_ok=True)
        self.plot_per_class(output_dir, method=method)
        self.plot_overlap(output_dir, method)
        self.plot_separability_heatmap(output_dir)

    def plot_per_class(self, output_dir: str,
                       method: str ) -> None:
        """
        One figure per class: histogram of each feature with all candidate
        trapezoids overlaid.
        """
        if self.candidates is None:
            raise RuntimeError("Call compute_trapezoid_candidates() first.")

        cand = self.candidates[self.candidates["method"] == method]
        for cls_id, group in self.df.groupby("class"):
            cls_name = self._class_name(cls_id)
            fig, axes = plt.subplots(1, len(Feature),
                                     figsize=(4 * len(Feature), 4))

            for ax, feat in zip(axes, Feature):
                csv_col = FEATURE_TO_CSV[feat]
                values = group[csv_col].dropna().values
                ax.hist(values, bins=30, alpha=0.6,
                        color=self._class_colour(cls_id),
                        edgecolor="white", linewidth=0.5)

                # Overlay recommended trapezoid
                row = cand[(cand["class_index"] == cls_id)
                           & (cand["feature"] == feat.name)]
                if len(row) > 0:
                    r = row.iloc[0]
                    ax.plot([r["a"], r["b"], r["c"], r["d"]],
                            [0, 1, 1, 0], "k-", linewidth=2,
                            label=f"{method} trapezoid")
                    ax.axvline(r["a"], color="gray", linestyle=":", alpha=0.7)
                    ax.axvline(r["d"], color="gray", linestyle=":", alpha=0.7)
                    ax.legend(fontsize=8)

                unit = FEATURE_UNITS.get(feat, "")
                ax.set_xlabel(f"{feat.nameStr} [{unit}]", fontsize=9)
                ax.set_ylabel("Frequency", fontsize=9)
                ax.set_title(feat.nameStr, fontsize=10, fontweight="bold")
                ax.grid(alpha=0.3, linestyle="--")

            fig.suptitle(f"{cls_name} (class {cls_id}, n={len(group)})",
                         fontsize=13, fontweight="bold")
            fig.tight_layout()
            fname = f"{output_dir}/class_{cls_id:02d}_{cls_name}.png"
            fig.savefig(fname, dpi=150, bbox_inches="tight")
            plt.close(fig)

        print(f"Wrote per-class diagnostics to {output_dir}/")

    def plot_overlap(self, output_dir: str, method: str) -> None:
        """One figure per feature showing all classes' trapezoids overlaid
        on a single shared axis (x = feature value, y = membership degree)."""
        if self.candidates is None:
            raise RuntimeError("Call compute_trapezoid_candidates() first.")

        cand = self.candidates[self.candidates["method"] == method]

        for feat in Feature:
            fig, ax = plt.subplots(figsize=(10, 3))
            feat_cand = cand[cand["feature"] == feat.name]

            for _, row in feat_cand.sort_values("class_index").iterrows():
                cls_id = int(row["class_index"])
                colour = self._class_colour(cls_id)
                label = f"{cls_id}: {self._class_name(cls_id)}"

                xs = [row["a"], row["b"], row["c"], row["d"]]
                ys = [0, 1, 1, 0]

                # Solid outline in the class colour (also carries the legend entry)
                ax.plot(xs, ys, color=colour, linewidth=2, label=label)

            unit = FEATURE_UNITS.get(feat, "")
            ax.set_xlabel(f"{feat.nameStr}", fontsize=11)
            ax.set_ylabel("Membership Degree", fontsize=11)
            ax.set_ylim(-0.02, 1.25)
            ax.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
            ax.set_title(f"Membership Trapezoids as predicted by {feat.nameStr}", fontsize=12)
            ax.grid(alpha=0.3, linestyle="--")
            ax.legend(fontsize=9, loc="center left",
                    bbox_to_anchor=(1.01, 0.5), frameon=False)
            fig.tight_layout()
            fname = f"{output_dir}/overlap_{feat.name}.png"
            fig.savefig(fname, dpi=150, bbox_inches="tight")
            plt.close(fig)

        print(f"Wrote overlap diagnostics to {output_dir}/")

    def plot_separability_heatmap(self, output_dir: str) -> None:
        """Heatmap of Fisher ratios: class pair x feature."""
        if self.separability is None:
            raise RuntimeError("Call compute_separability() first.")

        sepa = self.separability.copy()
        sepa["pair"] = sepa["class_a_name"] + " vs " + sepa["class_b_name"]
        pivot = sepa.pivot_table(
            index="pair", columns="feature", values="fisher_ratio"
        )

        fig, ax = plt.subplots(figsize=(9, max(4, 0.4 * len(pivot))))
        im = ax.imshow(pivot.values, cmap="viridis", aspect="auto")
        ax.set_xticks(range(len(pivot.columns)))
        ax.set_xticklabels(pivot.columns, rotation=30, ha="right", fontsize=9)
        ax.set_yticks(range(len(pivot.index)))
        ax.set_yticklabels(pivot.index, fontsize=8)
        for i in range(len(pivot.index)):
            for j in range(len(pivot.columns)):
                v = pivot.values[i, j]
                if np.isfinite(v):
                    ax.text(j, i, f"{v:.2f}", ha="center", va="center",
                            color="white" if v < np.nanmax(pivot.values) * 0.5
                            else "black", fontsize=8)
        plt.colorbar(im, ax=ax, label="Fisher discriminant ratio")
        ax.set_title("Class Separability per Feature",
                     fontsize=12, fontweight="bold")
        fig.tight_layout()
        fname = f"{output_dir}/separability_heatmap.png"
        fig.savefig(fname, dpi=150, bbox_inches="tight")
        plt.close(fig)
        print(f"Wrote separability heatmap to {output_dir}/")

    # -----------------------------------------------------------------
    # Report
    # -----------------------------------------------------------------
    def print_report(self) -> None:
        """Print a human-readable summary to stdout."""
        if self.statistics is None:
            raise RuntimeError("Call compute_statistics() first.")

        print("\n" + "=" * 78)
        print("syCAMOR CLASS SIGNATURE SUMMARY")
        print("=" * 78)
        print(f"Polarisation: {self.polarisation}")
        print(f"Total rows: {len(self.df) if self.df is not None else 0}")

        # Sample counts per class
        print("\n--- Sample counts per class ---")
        for cls_id, group in self.df.groupby("class"):
            cls_name = self._class_name(cls_id)
            n = len(group)
            flag = ""
            if n < MIN_SAMPLES_FAIL:
                flag = "  [INSUFFICIENT]"
            elif n < MIN_SAMPLES_WARN:
                flag = "  [LOW]"
            print(f"  {cls_id}: {cls_name:<25} n={n:>5}{flag}")

        # Per-class trapezoid candidates (standard method)
        if self.candidates is not None and "standard" in self.candidates["method"].values:
            print("\n--- Recommended trapezoids (method=standard) ---")
            std = self.candidates[self.candidates["method"] == "standard"]
            for cls_id, group in std.groupby("class_index"):
                cls_name = self._class_name(cls_id)
                print(f"\n  {cls_id}: {cls_name}")
                for _, row in group.iterrows():
                    feat = row["feature"]
                    print(f"    {feat:<22} "
                          f"[{row['a']:>8.3f}, {row['b']:>8.3f}, "
                          f"{row['c']:>8.3f}, {row['d']:>8.3f}]  "
                          f"(core width={row['core_width']:.3f})")

        # Overlap warnings
        if self.overlaps is not None:
            print("\n--- High-overlap class pairs (core_overlap_ratio > 0.5) ---")
            high = self.overlaps[self.overlaps["core_overlap_ratio"] > 0.5]
            if len(high) == 0:
                print("  None")
            else:
                for _, row in high.sort_values("core_overlap_ratio",
                                               ascending=False).iterrows():
                    print(f"  {row['class_a_name']:<20} vs "
                          f"{row['class_b_name']:<20} on {row['feature']:<22} "
                          f"overlap={row['core_overlap_ratio']:.2f}")

        # Best features per class pair
        if self.separability is not None:
            print("\n--- Best separating feature per class pair ---")
            best = (self.separability
                    .sort_values("fisher_ratio", ascending=False)
                    .groupby(["class_a_name", "class_b_name"])
                    .head(1))
            for _, row in best.iterrows():
                print(f"  {row['class_a_name']:<20} vs "
                      f"{row['class_b_name']:<20} -> "
                      f"{row['feature']:<22} (F={row['fisher_ratio']:.2f})")

        print("\n" + "=" * 78)

    # -----------------------------------------------------------------
    # Helpers
    # -----------------------------------------------------------------
    @staticmethod
    def _class_name(cls_id: int) -> str:
        """Map a class index to its enum name."""
        try:
            return LandClass.from_index(cls_id).displayName
        except (ValueError, KeyError):
            return f"CLASS_{cls_id}"

    @staticmethod
    def _class_colour(cls_id: int) -> str:
        """Map a class index to its enum colour."""
        try:
            
            return LandClass.from_index(cls_id).colour
        except (ValueError, KeyError):
            return "#888888"

    



def summariseTrainingSet():
    polarisation = "VV" #["VV", "VH", "both"]
    method = "narrow"
    outdir ="results/records/sigOutputs"

    s = (ClassSignatureSummariser("results/records/data.csv")
         .load(polarisation=polarisation)
         .compute_statistics()
         .compute_trapezoid_candidates()
         .compute_overlaps(method=method)
         .compute_separability()
         .compute_feature_weights()
         .recommend(method=method))

    s.export_statistics(f"{outdir}/statistics.csv")
    s.export_candidates(f"{outdir}/trapezoid_candidates.csv")
    s.export_overlaps(f"{outdir}/overlaps.csv")
    s.export_separability(f"{outdir}/separability.csv")
    s.export_feature_weights(f"{outdir}/feature_weights.csv")
    s.export_signature(f"{outdir}/json/signatures_{method}_{str(datetime.now().strftime("%Y%m%d_%H%M%S"))}.json")
    s.export_python_literal(f"{outdir}/signatures.py")
    s.plot_all(outdir, method)
    s.print_report()

if __name__ == "__main__":
    summariseTrainingSet()
