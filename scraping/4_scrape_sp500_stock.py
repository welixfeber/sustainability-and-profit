import os
import time
import requests
import pandas as pd
from datetime import date, timedelta
from threading import Thread
from math import ceil

# ─── CONFIG ───────────────────────────────────────────────
API_KEYS   = [
    "QMcafuvkWdOwyuj9hvDeQTBhqnjU37S1",
    "GTRDBsHqJV7laW2SZ73GKWx2w02o4gcj",
    "YTYrzzz6bsm0EFE5cAJtNmiU9BDHZDTo",
    "zKKIEq6EbNHihMYmF9aNMmRmvIHadoGM"
]
BASE_URL   = "https://financialmodelingprep.com/api/v3"
PAUSE_SEC  = 12                       # free tier: 5 calls/minute per key
OUTPUT_ALL = "sp500_prices_5y.csv"
CHECKPOINT_EVERY = 10                 # merge checkpoint every 10 symbols
# ─────────────────────────────────────────────────────────────

def get_sp500_tickers():
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    df = pd.read_html(url)[0]
    return df["Symbol"].tolist()

def load_scraped_symbols(filename):
    if not os.path.exists(filename):
        return set()
    df = pd.read_csv(filename, usecols=["symbol"])
    return set(df["symbol"].astype(str))

def fetch_prices(symbol, start, end, api_key):
    url = f"{BASE_URL}/historical-price-full/{symbol}"
    params = {"from": start, "to": end, "apikey": api_key}
    r = requests.get(url, params=params, timeout=10)
    r.raise_for_status()
    hist = r.json().get("historical", []) or []
    return [{"symbol": symbol, "date": x["date"], "close": x["close"]} for x in hist]

def scrape_subset(tickers, api_key, out_csv):
    today     = date.today()
    start_str = (today - timedelta(days=5*365)).isoformat()
    end_str   = today.isoformat()

    scraped = load_scraped_symbols(out_csv)
    # ensure file exists
    if not os.path.exists(out_csv):
        pd.DataFrame(columns=["symbol","date","close"]) \
          .to_csv(out_csv, index=False)

    counter = 0
    for sym in tickers:
        if sym in scraped:
            print(f"[{api_key}] Skipping {sym}")
            continue

        print(f"[{api_key}] Fetching {sym}…", end=" ")
        try:
            recs = fetch_prices(sym, start_str, end_str, api_key)
            if recs:
                pd.DataFrame(recs).to_csv(out_csv, mode="a", header=False, index=False)
                print(f"{len(recs)} pts")
            else:
                print("0 pts")
        except Exception as e:
            print(f"ERROR: {e.__class__.__name__}")
        scraped.add(sym)
        counter += 1

        # checkpoint merge
        if counter % CHECKPOINT_EVERY == 0:
            parts = []
            for i in range(len(API_KEYS)):
                fn = f"prices_part{i+1}.csv"
                if os.path.exists(fn):
                    parts.append(pd.read_csv(fn))
            if parts:
                pd.concat(parts, ignore_index=True) \
                  .to_csv(OUTPUT_ALL, index=False)
                print(f"[{api_key}] 🔄 checkpoint wrote {OUTPUT_ALL}")

        time.sleep(PAUSE_SEC)

    print(f"[{api_key}] DONE writing {out_csv}")

def main():
    tickers = get_sp500_tickers()
    n = len(tickers)
    k = len(API_KEYS)
    chunk = ceil(n / k)

    threads = []
    for i, api_key in enumerate(API_KEYS):
        subset = tickers[i*chunk:(i+1)*chunk]
        out_csv = f"prices_part{i+1}.csv"
        t = Thread(target=scrape_subset, args=(subset, api_key, out_csv), daemon=True)
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    # final merge
    dfs = []
    for i in range(len(API_KEYS)):
        fn = f"prices_part{i+1}.csv"
        if os.path.exists(fn):
            dfs.append(pd.read_csv(fn))
    if dfs:
        pd.concat(dfs, ignore_index=True) \
          .to_csv(OUTPUT_ALL, index=False)
        print(f"\n✅ Combined all parts into {OUTPUT_ALL}")

if __name__ == "__main__":
    main()

