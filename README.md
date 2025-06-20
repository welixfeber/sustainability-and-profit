**FIM Application Data Processing \- Felix Nicolas Weber**

- ESG Source: [https://app.gigasheet.com/spreadsheet/sp-500-esg-risk-ratings/c4866f1c\_c239\_4114\_9d92\_bf1d0dcb1b53](https://app.gigasheet.com/spreadsheet/sp-500-esg-risk-ratings/c4866f1c_c239_4114_9d92_bf1d0dcb1b53)  
- Auch Sektoren, etc. beinhaltet

- Profitmargin Source: [https://site.financialmodelingprep.com/developer/docs/stable](https://site.financialmodelingprep.com/developer/docs/stable)  
- Profit Margins spread over five years

Working document is combined with profit margins and ESG, into “sp500\_margins\_with\_esg”

- merge documents and remove all rows which are missing values in column "Total ESG Risk score"  
- left with 2035 value rows.  
- calculated regression models with regression\_total\_esg\_profit.py, results saved in esg\_margin\_results.txt  
  `Total ESG Risk score is significantly negatively related to net and gross profit margins, but not to operating margins:`  
* `Correlations`

  * `Net: –0.116`

  * `Gross: –0.161`

  * `Oper: –0.066`

* `OLS regressions (robust SE)`

  * `Net margin ≈ 0.186 – 0.002 × ESG (p = 0.019)`

  * `Gross margin ≈ 0.635 – 0.0057 × ESG (p = 0.0007)`

  * `Operating margin ≈ 0.222 – 0.0013 × ESG (p = 0.17, n.s.)`

  `In plain terms: a one-point higher ESG-risk score is associated with about a 0.2 pp drop in net margin and a 0.6 pp drop in gross margin, both statistically significant. There’s no clear relationship with operating margin.`

- all esg correlations calculated in regression\_all\_esg\_metrics.py, results in esg\_subscores\_correlations.csv

## **1\) What the correlations tell us**

| ESG Sub-score | Net margin | Gross margin | Oper margin |
| ----- | ----- | ----- | ----- |
| **Total ESG Risk** | –0.116 | –0.161 | –0.066 |
| **Environment Risk** | –0.131 | **–0.402** | –0.078 |
| **Social Risk** | –0.075 | \+0.027 | –0.053 |
| **Governance Risk** | \+0.065 | \+0.399 | \+0.062 |
| **Controversy Score** | **–0.153** | –0.145 | **–0.107** |

*   
  The **strongest negative** link is between **Environment Risk** and **Gross margin** (r≈–0.40).

* **Controversy Score** also has a moderate negative tie to **Net margin** (r≈–0.15).

* Surprisingly, **Governance Risk** correlates **positively** with Gross (r≈+0.40).

* **Social Risk** shows almost no relationship with any margin.

- OLS regression of those results in esg\_subscores\_regression.py, results in esg\_subscores\_regression.txt

**Takeaway:**

- Companies with **higher controversy risk** (i.e. more severe negative incidents) tend to have **significantly lower** profit margins, even after accounting for their environmental, social, and governance risk scores. The other ESG dimensions by themselves correlate with profitability, but their effects overlap so much that only controversy stands out in a joint model.

\-barplot from plotting\_esg\_profit.py

![][image1]

- result of percentile\_plots.py:

![][image2]

- plot\_margins\_by\_percentile.py  
- ![][image3]

- plot\_esgscore\_margins.py  
  ![][image4]  
    
  plot\_trendline\_margins.py:  
  ![][image5]  
    
- to remove outliers: plot\_binned\_profitmargins  
- ![][image6]

**Scraping S\&P500 Stock**

- using **4\_scrape\_sp500\_stock.py** to scrape s\&p500 stock over the last 5 years, roughly 1255 entries per stock.

**How to continue:**

- normalize stock prices to start day (5/26/2020) \= 1 using normalize\_stock.py, saved in sp500\_prices\_5y\_normalized.csv  
- merge with previous file, which will give us normalized stock prices \+ esg score. remove any rows with missing values  
- 510,785 rows left.  
  merged using merge\_norm\_stock\_esg.py, saved in sp500\_prices\_with\_esg.csv.   
- plotted development of stock values over time, grouped by ESG risk level group in plot\_stock\_development\_riskgroups.py  
-   
- analyze correlation and causation between factors, relationship between esg risk score group and stock price development.  
  ![][image7]  
- same for low, medium, high risk levels. plot\_stock\_development\_risk\_lowmedhigh.py

  ![][image8]

  stock\_volatility.py to show volatility by risk group

  ![][image9]

- calculate statistical tests with calculate\_relationship\_stock\_esg.py:  
  results in relationship\_stock\_esg.txt

The results show **no meaningful relationship** between a company’s Total ESG Risk score and its **current** normalized stock price:

* **Pearson r \= 0.069**: a very weak positive correlation.

* **p ≈ 0.27**: far above the usual 0.05 threshold, so we cannot reject the null of zero correlation.

* **R² ≈ 0.5 %** in the OLS regression: ESG score explains essentially none of the cross‐sectional variation in normalized price.

* **Slope ≈ \+0.013** (p ≈ 0.27): each one‐point higher ESG risk is associated with a 1.3 % higher normalized price, but this estimate is not statistically significant.  
- 

**Heatmap to find correlations:** heatmap\_plot.py

![][image10]

**ESG sub-scores are highly collinear.**

* Total ESG Risk is almost perfectly correlated with Environment (≈0.75) and Social (≈0.69), and strongly with Controversy (≈0.37).

* Governance stands a bit apart, correlating negatively with Environment (≈–0.18) but positively with Social (≈0.38).

**Profit-margin metrics cluster tightly.**

* Net, Gross and Operating margins all inter-correlate above 0.40, and each also correlates positively with cumulative return (≈0.5 for net & gross).

* Operating margin and net margin both have a moderate positive link with ESG risk (≈0.2–0.3), but note that once you control for controversy earlier these effects disappeared.

**Returns vs. Volatility.**

* Cumulative return shows a small positive relationship with ESG risk (≈0.1), but virtually zero with Governance risk.

* Volatility is mildly higher for higher-risk firms (≈0.15 with ESG total, ≈0.1 with controversy).

**Small heatmap:** small\_heatmap\_plot.py

That “ESG vs Profit & Stock” heatmap tells the story cleanly:

* **Governance Risk Score** is **positively** correlated with **gross profit margin** (\~ \+0.45).

* **Environment Risk Score** shows a **negative** link to gross margin (\~ –0.40).

* All ESG dimensions have small **positive** ties to **cumulative return** (\~ \+0.1–+0.2).

* **Controversy Score** is mildly **negatively** correlated with **net margin** (\~ –0.15).

* Higher ESG Risk tends to go with slightly higher **volatility** (\~ \+0.15).

**File to compute cummulative returns and volatility:** compute\_returns\_volatility.py, saved in sp500\_prices\_with\_esg\_plus\_returns.csv

Then plotted esg correlations by industry; plot\_esg\_by\_industry.py

- calculate correlations and statistical significance with significance\_esg\_stock\_by\_sector.py  
- results saved in sector\_esg\_stock\_significance.csv

using heatmap\_esg\_profit\_by\_sector.py, we see correlation between esg factors and profit margins by industrial sector.
