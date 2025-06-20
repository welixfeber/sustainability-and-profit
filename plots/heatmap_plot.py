import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ─── CONFIG ───────────────────────────────────────────────
PRICE_FILE = "sp500_prices_with_esg.csv"  # normalized price + ESG metadata (daily)
MARGIN_FILE = "sp500_margins_with_esg.csv"  # profit margins + ESG metadata (annual)
OUTPUT_HEAT = "correlation_heatmap.png"  # optional: save figure


# ─────────────────────────────────────────────────────────────

def main():
    # 1) Load daily normalized prices with ESG
    df_price = pd.read_csv(PRICE_FILE, parse_dates=["date"])
    df_price = df_price.dropna(subset=["normalized_price", "Total ESG Risk score"])

    # 2) Compute per‐symbol features
    # 2a) Daily returns
    df_price = df_price.sort_values(["symbol", "date"])
    df_price["daily_return"] = df_price.groupby("symbol")["normalized_price"].pct_change()

    # 2b) 30‐day rolling volatility
    df_price["volatility"] = (
        df_price
        .groupby("symbol")["daily_return"]
        .rolling(window=30, min_periods=15)
        .std()
        .reset_index(level=0, drop=True)
    )

    # 2c) Cumulative return = last normalized_price − 1
    cum_ret = df_price.groupby("symbol")["normalized_price"].last().rename("cum_return")

    # 2d) Recent volatility = last rolling vol (to align with other cross‐sectional vars)
    recent_vol = df_price.groupby("symbol")["volatility"].last().rename("volatility")

    # 3) Load annual profit margins + ESG from margins file
    df_margin = pd.read_csv(MARGIN_FILE, parse_dates=["date"])
    df_margin = df_margin.sort_values("date").groupby("symbol", as_index=False).last()
    df_margin = df_margin.set_index("symbol")

    # 4) Extract ESG sub‐scores & profit margins
    esg_cols = ["Total ESG Risk score",
                "Environment Risk Score",
                "Social Risk Score",
                "Governance Risk Score",
                "Controversy Score"]
    marg_cols = ["netProfitMargin",
                 "grossProfitMargin",
                 "operatingProfitMargin"]
    df_esg = df_margin[esg_cols]
    df_margins = df_margin[marg_cols]

    # 5) Combine into a single cross‐sectional DataFrame
    df_cs = pd.concat(
        [df_esg, df_margins, cum_ret, recent_vol],
        axis=1
    ).dropna()

    # 6) Compute correlation matrix
    corr = df_cs.corr()

    # 7) Plot heatmap using matplotlib
    labels = corr.columns
    fig, ax = plt.subplots(figsize=(10, 8))
    im = ax.imshow(corr.values, cmap="coolwarm", vmin=-1, vmax=1)

    # Axis ticks and labels
    ax.set_xticks(np.arange(len(labels)))
    ax.set_yticks(np.arange(len(labels)))
    ax.set_xticklabels(labels, rotation=45, ha="right")
    ax.set_yticklabels(labels)

    # Colorbar
    cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label("Pearson correlation")

    plt.title("Cross‐Sectional Correlation Heatmap\nESG, Profit Margins, Return & Volatility")
    plt.tight_layout()
    plt.savefig(OUTPUT_HEAT, dpi=300)
    plt.show()


if __name__ == "__main__":
    main()
