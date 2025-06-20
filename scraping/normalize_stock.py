import pandas as pd

# ─── CONFIG ───────────────────────────────────────────────
INPUT_FILE = "sp500_prices_5y.csv"
OUTPUT_FILE = "sp500_prices_5y_normalized.csv"
START_DATE = "2020-05-26"  # first trading day in your 5y window


# ─────────────────────────────────────────────────────────────

def main():
    # 1) Load daily prices
    df = pd.read_csv(INPUT_FILE, parse_dates=["date"])

    # 2) Keep only from START_DATE onward (inclusive)
    df = df[df["date"] >= pd.Timestamp(START_DATE)].copy()

    # 3) Sort so that .iloc[0] is the first available price per symbol
    df = df.sort_values(["symbol", "date"])

    # 4) Normalize: first 'close' per symbol → 1
    df["normalized_price"] = (
        df
        .groupby("symbol")["close"]
        .transform(lambda x: x / x.iloc[0])
    )

    # 5) Save
    df.to_csv(OUTPUT_FILE, index=False)
    print(f"✅ Saved normalized prices to {OUTPUT_FILE}")
    # optional: show a preview
    print(df.groupby("symbol").first().reset_index()[["symbol", "date", "normalized_price"]].head())


if __name__ == "__main__":
    main()