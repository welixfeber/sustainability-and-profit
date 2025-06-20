import pandas as pd
import statsmodels.api as sm

# ─── CONFIG ───────────────────────────────────────────────
MERGED_FILE = "sp500_margins_with_esg.csv"  # your merged margins+ESG file
OUTPUT_FILE = "esg_margin_results.txt"  # where we’ll dump summaries


# ─────────────────────────────────────────────────────────────

def main():
    # 1) Load merged data
    df = pd.read_csv(MERGED_FILE, parse_dates=["date"])

    # 2) For each symbol keep the most recent profit‐margin row
    df_latest = (
        df.sort_values("date")
        .groupby("symbol", as_index=False)
        .last()
    )

    # 3) Rename for convenience
    df_latest = df_latest.rename(columns={
        "Total ESG Risk score": "esg_total",
        "netProfitMargin": "net",
        "grossProfitMargin": "gross",
        "operatingProfitMargin": "oper"
    })

    # 4) Drop any symbols missing either ESG or margins
    df_cs = df_latest[["symbol", "esg_total", "net", "gross", "oper"]].dropna()

    # 5) Compute Pearson correlations
    corr = df_cs[["esg_total", "net", "gross", "oper"]].corr()

    # 6) Run separate OLS regressions:
    X = sm.add_constant(df_cs["esg_total"])
    results = {
        "net": sm.OLS(df_cs["net"], X).fit(cov_type="HC0"),
        "gross": sm.OLS(df_cs["gross"], X).fit(cov_type="HC0"),
        "oper": sm.OLS(df_cs["oper"], X).fit(cov_type="HC0")
    }

    # 7) Output everything to a text file
    with open(OUTPUT_FILE, "w") as f:
        f.write("=== Pearson Correlations ===\n")
        f.write(corr.to_string())
        f.write("\n\n")
        for name, res in results.items():
            f.write(f"=== OLS Regression: profit margin = {name} ===\n")
            f.write(res.summary().as_text())
            f.write("\n\n")

    print(f"Done. Correlations and regressions written to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
