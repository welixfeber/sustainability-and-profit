import os
import warnings
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# ─── CONFIG ─────────────────────────────────────────────────────
PRICE_RET_FILE = "sp500_prices_with_esg_plus_returns.csv"
MARGIN_FILE    = "sp500_margins_with_esg.csv"
OUTPUT_FOLDER  = "sector_heatmaps"
MIN_PAIRS      = 8     # minimum observations per ESG×metric to compute r
# ESG dimensions to include (must match column names)
DESIRED_ESG    = [
    "Total ESG Risk score",
    "Environment Risk Score",
    "Social Risk Score",
    "Governance Risk Score",
    "Controversy Score",
]
# Metrics: profit margins plus price-based metrics
DESIRED_METRICS = [
    "netProfitMargin",
    "grossProfitMargin",
    "operatingProfitMargin",
    "cum_return",
    "volatility",
]
# ────────────────────────────────────────────────────────────────

# 1) Check inputs exist
for fn in (PRICE_RET_FILE, MARGIN_FILE):
    if not os.path.exists(fn):
        raise FileNotFoundError(f"Could not find {fn!r}")

# 2) Load price+ESG+returns
df_pr = pd.read_csv(PRICE_RET_FILE, parse_dates=["date"], low_memory=False)
# take last row per symbol (contains cum_return, volatility, ESG, Industry)
df_pr_last = (
    df_pr
    .sort_values(["symbol", "date"])
    .groupby("symbol", as_index=False)
    .last()
)

# 3) Load margins+ESG
df_m = pd.read_csv(MARGIN_FILE, parse_dates=["date"], low_memory=False)
# take last row per symbol (contains margins)
df_m_last = (
    df_m
    .sort_values(["symbol", "date"])
    .groupby("symbol", as_index=False)
    .last()
)

# 4) Merge cross‐section: price+returns+ESG+Industry + margins
df = pd.merge(
    df_pr_last,
    df_m_last[["symbol", "netProfitMargin", "grossProfitMargin", "operatingProfitMargin"]],
    on="symbol",
    how="inner"
)
df = df.dropna(subset=["Sector"])  # ensure Industry present

# 5) Determine which columns we actually have
ESG_COLS    = [c for c in DESIRED_ESG    if c in df.columns]
METRIC_COLS = [c for c in DESIRED_METRICS if c in df.columns]

if not ESG_COLS or not METRIC_COLS:
    raise ValueError("No valid ESG or metric columns found in merged data.")

# 6) Prepare output folder
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# 7) Loop over each Industry and build heatmap
for sector, grp in df.groupby("Sector"):
    n = len(grp)
    if n < MIN_PAIRS:
        continue

    # build empty corr matrix
    corr = pd.DataFrame(index=ESG_COLS, columns=METRIC_COLS, dtype=float)

    # compute Pearson r only if enough non-NA pairs exist
    for e in ESG_COLS:
        for m in METRIC_COLS:
            valid = grp[[e, m]].dropna()
            corr.loc[e, m] = valid[e].corr(valid[m]) if len(valid) >= MIN_PAIRS else np.nan

    # drop any ESG rows or metric cols that are entirely NaN
    corr = corr.dropna(how="all", axis=0).dropna(how="all", axis=1)
    if corr.empty:
        continue

    # plot
    plt.figure(figsize=(8, 6))
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=RuntimeWarning)
        sns.heatmap(
            corr.astype(float),
            annot=True,
            fmt=".2f",
            cmap="RdBu_r",
            vmin=-1, vmax=1,
            cbar_kws={"label": "Pearson r"},
        )
    plt.title(f"{sector} (n={n})")
    plt.xticks(rotation=45, ha="right")
    plt.yticks(rotation=0)
    plt.tight_layout()

    # save
    safe = sector.replace("/", "_").replace(" ", "_")
    plt.savefig(f"{OUTPUT_FOLDER}/heatmap_{safe}.png", dpi=150)
    plt.close()

print("✅ All sector heatmaps saved to", OUTPUT_FOLDER)