# Stock price reader

A small Python 3.9+ foundation using pandas for CSV loading, sorting, and grouping, with three functions in `Data_reader.py`:

- `read_prices(path)` returns a dictionary mapping each company to a NumPy price array, sorted by date ascending.
- `select_companies(prices_by_company, companies)` returns a smaller dictionary containing only the requested companies.
- `plot_prices(prices_by_company)` plots every company in a dictionary on one chart and returns the Matplotlib axes. Call `plt.show()` to display it or `ax.figure.savefig("prices.png")` to save it.

Install and run:

```sh
python -m pip install -r requirements.txt
python Data_reader.py example_prices.csv AAPL MSFT
```

The example CSV contains fictional prices. Supply one observation per row:

```csv
company,date,close
AAPL,2026-01-02,250.00
AAPL,2026-01-05,252.00
```

Use it from Python:

```python
import matplotlib.pyplot as plt
from Data_reader import read_prices, select_companies, plot_prices

prices = read_prices("example_prices.csv")
chosen_prices = select_companies(prices, ["AAPL", "MSFT"])
plot_prices(chosen_prices)
plt.show()
```

To plot all companies in the CSV, pass the full dictionary directly:

```python
plot_prices(prices)
```

For different headers or dates, pass column names and a `strptime` date format:

```python
prices = read_prices(
    "stocks.csv",
    company_column="Ticker",
    date_column="Date",
    price_column="Adj Close",
    date_format="%d/%m/%Y",
)
```

Index 0 is the earliest observation for that company. Missing trading days are not filled, and indices across companies do not necessarily refer to the same date. Duplicate dates retain their CSV order. Dates are used for sorting and are not included in the returned arrays. Use consistently adjusted prices if you want to account for stock splits or dividends.

Missing columns, empty values, and invalid dates or prices raise `ValueError`. A header-only CSV returns an empty dictionary.

## Downloading Egyptian Exchange data

`egx_downloader.py` is a small collection script for Yahoo Finance data. It uses
the `yfinance` package, which sends requests to Yahoo Finance and returns the
answer as a Pandas table. No API key is required, but it is an unofficial data
source: check the returned CSV before relying on it for research or decisions.

First install the packages inside the project's virtual environment:

```sh
.venv/bin/python -m pip install -r requirements.txt
```

Then start with two symbols. Many Egyptian Exchange symbols use `.CA` on Yahoo
Finance, but confirm the exact symbol on the Yahoo Finance website first:

```sh
.venv/bin/python egx_downloader.py COMI.CA HRHO.CA
```

This creates `egx_prices.csv` with these columns:

```text
company,date,open,high,low,close,adj_close,volume
```

`start` is included and `end` is excluded. The defaults request 1 November
2016 through 1 November 2026, so the default end is `2026-11-02`.

Use the saved CSV with the plotting program:

```python
import matplotlib.pyplot as plt
from Data_reader import read_prices, select_companies, plot_prices

prices = read_prices("egx_prices.csv")
chosen_prices = select_companies(prices, ["COMI.CA", "HRHO.CA"])
plot_prices(chosen_prices)
plt.show()
```

The downloader deliberately requests one company at a time and waits one second
between requests. That is slower, but it makes failures easier to see and helps
avoid overwhelming a free data source. It saves only successful companies and
then prints a coverage report. A short history or a missing company is a result
to investigate, not proof that the stock did not trade.
