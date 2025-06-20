import pandas as pd

# ─── CONFIG ───────────────────────────────────────────────
PRICE_FILE   = "sp500_prices_5y_normalized.csv"    # your normalized prices
ESG_FILE     = "20250521_sp500_esg_score.csv"      # ESG metadata file
OUTPUT_FILE  = "sp500_prices_with_esg.csv"         # merged output
# ─────────────────────────────────────────────────────────────

def main():
    # 1) Load normalized prices
    df_price = pd.read_csv(PRICE_FILE, parse_dates=["date"])
    df_price["symbol"] = df_price["symbol"].astype(str).str.strip().str.upper()

    # 2) Load ESG metadata
    df_esg = pd.read_csv(ESG_FILE)
    df_esg = df_esg.rename(columns={"Symbol": "symbol"})
    df_esg["symbol"] = df_esg["symbol"].astype(str).str.strip().str.upper()

    # 3) Merge on symbol, keep all price rows
    df_merged = pd.merge(
        df_price,
        df_esg,
        on="symbol",
        how="left"
    )

    # 4) Drop rows where Total ESG Risk score is missing
    df_merged = df_merged[df_merged["Total ESG Risk score"].notna()].reset_index(drop=True)

    # 5) Save
    df_merged.to_csv(OUTPUT_FILE, index=False)
    print(f"✅ Saved merged file with {len(df_merged)} rows to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()