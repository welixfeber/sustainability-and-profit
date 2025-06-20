import pandas as pd

# ─── CONFIG ───────────────────────────────────────────────
MERGED_FILE = "sp500_margins_with_esg.csv"  # your merged CSV
OUTPUT_FILE = "esg_subscores_correlations.csv"


# ─────────────────────────────────────────────────────────────

def main():
    # 1) Load merged data
    df = pd.read_csv(MERGED_FILE, parse_dates=["date"])

    # 2) Keep only the most recent row per symbol
    df_latest = (
        df.sort_values("date")
        .groupby("symbol", as_index=False)
        .last()
    )

    # 3) Select the ESG sub‐scores and profit margins
    cols = [
        "Total ESG Risk score",
        "Environment Risk Score",
        "Social Risk Score",
        "Governance Risk Score",
        "Controversy Score",
        "netProfitMargin",
        "grossProfitMargin",
        "operatingProfitMargin"
    ]
    df_cs = df_latest[cols].dropna()

    # 4) Compute the Pearson correlation matrix
    corr = df_cs.corr()

    # 5) Save to CSV and print
    corr.to_csv(OUTPUT_FILE)
    print("Correlation matrix:")
    print(corr)
    print(f"\n✅ Saved correlation matrix to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
