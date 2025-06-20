# plot_esg_vs_margins_by_sector.py

import os
import warnings
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import pearsonr

# ─── CONFIG ─────────────────────────────────────────────────────
INPUT_FILE    = "sp500_margins_with_esg.csv"
OUTPUT_FOLDER = "sector_margin_heatmaps"
ALPHA         = 0.05

# ESG dimensions to include (must match exactly)
ESG_COLS = [
    "Total ESG Risk score",
    "Environment Risk Score",
    "Social Risk Score",
    "Governance Risk Score",
    "Controversy Score",
]

# Profit-margin metrics
PERF_COLS = [
    "netProfitMargin",
    "grossProfitMargin",
    "operatingProfitMargin",
]
# ────────────────────────────────────────────────────────────────

# 1) Load & clean
df = pd.read_csv(INPUT_FILE, parse_dates=["date"], low_memory=False)
df = df.dropna(subset=["Sector"])  # ensure sector present

# 2) Filter to only rows where both an ESG and at least one profit‐margin exist
keep = ESG_COLS + PERF_COLS
df = df.dropna(subset=ESG_COLS, how="all")  # at least one ESG
df = df.dropna(subset=PERF_COLS, how="all") # at least one margin

# 3) Prepare output folder
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# 4) Loop by sector
for sector, sub in df.groupby("Sector"):
    n = len(sub)
    if n < 5:
        # too few observations to correlate
        continue

    # 5) Compute r and p‐values
    r_mat = pd.DataFrame(index=ESG_COLS, columns=PERF_COLS, dtype=float)
    p_mat = pd.DataFrame(index=ESG_COLS, columns=PERF_COLS, dtype=float)

    for e in ESG_COLS:
        for m in PERF_COLS:
            block = sub[[e, m]].dropna()
            if len(block) >= 5:
                r, p = pearsonr(block[e], block[m])
            else:
                r, p = np.nan, np.nan
            r_mat.loc[e, m] = r
            p_mat.loc[e, m] = p

    # 6) Mask non-significant
    mask = p_mat > ALPHA

    # 7) Drop any rows/cols that are entirely NaN
    r_mat = r_mat.dropna(how="all", axis=0).dropna(how="all", axis=1)
    mask  = mask.loc[r_mat.index, r_mat.columns]

    if r_mat.empty:
        continue

    # 8) Plot
    plt.figure(figsize=(6, 5))
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=RuntimeWarning)
        sns.heatmap(
            r_mat.astype(float),
            mask=mask,
            annot=True,
            fmt=".2f",
            cmap="RdBu_r",
            vmin=-1, vmax=1,
            cbar_kws={"label": "Pearson r"},
        )
    plt.title(f"{sector} (n={n})\n(masked if p ≥ {ALPHA})")
    plt.xticks(rotation=30, ha="right")
    plt.yticks(rotation=0)
    plt.tight_layout()

    # 9) Save
    safe = sector.replace("/", "_").replace(" ", "_")
    plt.savefig(f"{OUTPUT_FOLDER}/heatmap_{safe}.png", dpi=150)
    plt.close()

print("✅ Sector‐level profit‐margin heatmaps saved to", OUTPUT_FOLDER)
