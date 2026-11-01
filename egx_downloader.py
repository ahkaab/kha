"""Download daily Egyptian Exchange prices from Yahoo Finance into a CSV file.

Yahoo Finance identifies many Egyptian shares with the ``.CA`` suffix. For
example, use ``COMI.CA`` for Commercial International Bank. Check the symbol
in Yahoo Finance before starting a large download.
"""

from __future__ import annotations

import time

import pandas as pd
import yfinance as yf

name_list = [
    'AALR.CA',
    'ABUK.CA',
    'ACGC.CA',
    'ADCI.CA',
    'COMI.CA',
    'DEIN.CA',
    'DOMT.CA',
    'EASB.CA',
    'EAST.CA',
    'EGAL.CA',
    'EGAS.CA'
]
def download_company(
    symbol: str,
    start: str,
    end: str,
) -> pd.DataFrame:
    """Download one company's daily OHLCV history.

    ``start`` is included; ``end`` is excluded by Yahoo Finance. For example,
    use end="2026-11-02" when you want to include 1 November 2026.
    """
    data = yf.download(
        symbol,
        start=start,
        end=end,
        interval="1d",
        auto_adjust=False,
        progress=False,
        threads=False,
        multi_level_index=False,
    )
    if data.empty:
        raise ValueError(f"No price data returned for {symbol}")

    data = data.reset_index()
    data.columns = [str(column).lower().replace(" ", "_") for column in data.columns]
    data.insert(0, "company", symbol)
    return data[["company", "date", "open", "high", "low", "close", "adj_close", "volume"]]


def download_companies(
    symbols: list[str],
    start: str,
    end: str,
    pause_seconds: float = 1.0,
) -> pd.DataFrame:
    """Download companies one at a time and combine successful results.

    Downloading sequentially with a short pause makes a large request less
    likely to be rate-limited. Failed symbols are printed and skipped so that
    the successful data can still be saved and inspected.
    """
    if not symbols:
        raise ValueError("Provide at least one Yahoo Finance symbol")

    histories = []
    for number, symbol in enumerate(symbols, start=1):
        try:
            history = download_company(symbol, start, end)
            histories.append(history)
            print(f"{number}/{len(symbols)}: downloaded {symbol} ({len(history)} rows)")
        except Exception as error:
            print(f"{number}/{len(symbols)}: skipped {symbol}: {error}")
        if number < len(symbols):
            time.sleep(pause_seconds)

    if not histories:
        raise RuntimeError("No companies were downloaded successfully")
    return pd.concat(histories, ignore_index=True).sort_values(["company", "date"])


def save_prices(prices: pd.DataFrame, path: str) -> None:
    """Save a downloaded price table as a CSV readable by Data_reader.py."""
    prices.to_csv(path, index=False)


def coverage_report(prices: pd.DataFrame) -> pd.DataFrame:
    """Return the first date, last date, and row count for each company."""
    return prices.groupby("company").agg(
        first_date=("date", "min"),
        last_date=("date", "max"),
        observations=("date", "size"),
    )
data_test = download_companies(name_list,'2018-01-01', '2026-10-31')
print(coverage_report(data_test))
save_prices( data_test,'/Users/adambarakat/Documents/kha/test_data.csv')


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("symbols", nargs="+", help="Yahoo Finance symbols, for example COMI.CA HRHO.CA")
    parser.add_argument("--start", default="2016-11-01", help="First date to request (YYYY-MM-DD)")
    parser.add_argument("--end", default="2026-11-02", help="First date to exclude (YYYY-MM-DD)")
    parser.add_argument("--output", default="egx_prices.csv", help="CSV file to create")
    args = parser.parse_args()

    prices = download_companies(args.symbols, args.start, args.end)
    save_prices(prices, args.output)
    print("\nCoverage report:")
    print(coverage_report(prices).to_string())
