import pandas as pd
import statsmodels.api as sm

# ─── CONFIG ───────────────────────────────────────────────
MERGED_FILE = "sp500_prices_with_esg.csv"  # merged normalized prices + ESG


# ─────────────────────────────────────────────────────────────

def main():
    # 1) Load merged data
    df = pd.read_csv(MERGED_FILE, parse_dates=["date"])

    # 2) For each symbol, keep the most recent normalized price
    df_latest = (
        df.sort_values("date")
        .groupby("symbol", as_index=False)
        .last()
    )

    # 3) Select and drop missing
    df_cs = df_latest[["Total ESG Risk score", "normalized_price"]].dropna()

    # 4) Pearson correlation
    corr = df_cs["Total ESG Risk score"].corr(df_cs["normalized_price"])
    print(f"Pearson correlation: {corr:.3f}\n")

    # 5) OLS regression: normalized_price ~ ESG total
    X = sm.add_constant(df_cs["Total ESG Risk score"])
    y = df_cs["normalized_price"]
    model = sm.OLS(y, X).fit(cov_type="HC0")

    print(model.summary())


if __name__ == "__main__":
    main()
