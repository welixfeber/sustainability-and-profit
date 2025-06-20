import pandas as pd
import statsmodels.api as sm

# ─── CONFIG ───────────────────────────────────────────────
DATA_FILE = "sp500_margins_with_esg.csv"  # merged file with all margins + ESG metadata
# ─────────────────────────────────────────────────────────────

def load_latest():
    df = pd.read_csv(DATA_FILE, parse_dates=["date"])
    # for each symbol, keep the last (most recent) row
    return df.sort_values("date").groupby("symbol", as_index=False).last()

def run_regression(df, dep_var, indep_vars):
    X = df[indep_vars]
    X = sm.add_constant(X)
    y = df[dep_var]
    model = sm.OLS(y, X).fit(cov_type="HC0")
    print(f"\n=== Regression: {dep_var} ~ {', '.join(indep_vars)} ===")
    print(model.summary())

def main():
    df = load_latest()
    # select only the columns we need, drop any rows with missing values
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
    df = df[cols].dropna()

    indep = [
        "Total ESG Risk score",
        "Environment Risk Score",
        "Social Risk Score",
        "Governance Risk Score",
        "Controversy Score"
    ]

    # Correlation matrix
    print("Pearson correlations:\n")
    print(df[indep + ["netProfitMargin","grossProfitMargin","operatingProfitMargin"]].corr())

    # Run regressions
    for dep in ["netProfitMargin","grossProfitMargin","operatingProfitMargin"]:
        run_regression(df, dep, indep)

if __name__ == "__main__":
    main()
