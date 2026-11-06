"""Load company price histories from CSV and plot them in observation order."""

from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.axes import Axes


def read_prices(
    path: str,
    company_column: str = "company",
    date_column: str = "date",
    price_column: str = "open",
    date_format: str = "%Y-%m-%d",
) -> tuple[dict[str, np.ndarray], np.ndarray]:
    """Return ``(prices_by_company, dates)`` with one shared sorted date axis.

    ``prices_by_company`` is the existing company -> price array dictionary.
    ``dates`` is a NumPy datetime array. Every company price array is aligned
    with that same date array; missing observations become ``NaN``.
    """
    data = pd.read_csv(path, dtype={company_column: "string"})
    required = {company_column, date_column, price_column}
    missing = required - set(data.columns)
    if missing:
        raise ValueError(f"Missing CSV columns: {', '.join(sorted(missing))}")

    # Clean the company names and convert dates and prices to usable types.
    data[company_column] = data[company_column].str.strip()
    data[date_column] = pd.to_datetime(data[date_column], format=date_format)
    data[price_column] = pd.to_numeric(data[price_column], errors="raise").astype(float)
    if data[list(required)].isna().any().any() or data[company_column].eq("").any():
        raise ValueError("Company, date, and price must not be empty")
    if not np.isfinite(data[price_column]).all():
        raise ValueError("Prices must be finite")
    duplicate_rows = data.duplicated([company_column, date_column], keep=False)
    if duplicate_rows.any():
        duplicate = data.loc[duplicate_rows, [company_column, date_column]].iloc[0]
        raise ValueError(
            "Duplicate company/date record: "
            f"{duplicate[company_column]} on {duplicate[date_column].date()}"
        )

    # Build one date axis, then align every company price array to that axis.
    dates = np.sort(data[date_column].unique())
    prices_by_company = {}
    for company, rows in data.groupby(company_column, sort=False):
        price_series = rows.set_index(date_column)[price_column]
        prices_by_company[company] = price_series.reindex(dates).to_numpy()
    return prices_by_company, dates


def read_open_close_prices(
    path: str,
) -> tuple[dict[str, np.ndarray], dict[str, np.ndarray], np.ndarray]:
    """Return aligned opens, closes, and dates, retaining complete dates only.

    Apply one shared mask to both fields so missing observations cannot shift
    the signal prices relative to the execution prices. No prices are filled.
    """
    open_prices, dates = read_prices(path, price_column="open")
    close_prices, close_dates = read_prices(path, price_column="close")
    if not open_prices:
        raise ValueError("Provide at least one company price array")
    if not np.array_equal(dates, close_dates):
        raise ValueError("Open and close dates must match")
    arrays = list(open_prices.values()) + list(close_prices.values())
    if any(np.any(prices[np.isfinite(prices)] <= 0) for prices in arrays):
        raise ValueError("Open and close prices must be positive")
    valid_dates = np.isfinite(np.vstack(arrays)).all(axis=0)
    if not valid_dates.any():
        raise ValueError("No dates have complete open and close prices")
    return (
        {company: prices[valid_dates] for company, prices in open_prices.items()},
        {company: prices[valid_dates] for company, prices in close_prices.items()},
        dates[valid_dates],
    )


def plot_prices(
    prices_by_company: dict[str, np.ndarray],
    dates: np.ndarray | None = None,
    ax: Axes | None = None,
) -> Axes:
    """Plot each company on a shared date axis, or observation indices."""
    plt.style.use('dark_background')
    if not prices_by_company:
        raise ValueError("Provide at least one company and price array")
    if ax is None:
        _, ax = plt.subplots(figsize=(10, 4), layout="constrained")
    if dates is not None:
        dates = np.asarray(dates)
        if dates.ndim != 1:
            raise ValueError("Dates must be a one-dimensional array")
    for company, prices in prices_by_company.items():
        values = np.asarray(prices, dtype=float)
        real_values = values[~np.isnan(values)]
        if values.ndim != 1 or values.size == 0 or real_values.size == 0 or not np.isfinite(real_values).all():
            raise ValueError(f"{company!r} must have a nonempty, one-dimensional numeric price array")
        if dates is not None and len(dates) != len(values):
            raise ValueError(f"{company!r} has {len(values)} prices but there are {len(dates)} dates")
        if dates is None:
            ax.plot(values, label=company, linewidth=1.8)
        else:
            ax.plot(dates, values, label=company, linewidth=1.8)
    x_label = "Date" if dates is not None else "Observation index (oldest → newest)"
    ax.set(title="Stock prices", xlabel=x_label, ylabel="Price")
    ax.grid(True, alpha=0.25)
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend()
    
    return ax


def select_companies(
    prices_by_company: dict[str, np.ndarray],
    companies: list[str],
) -> dict[str, np.ndarray]:
    """Return a smaller price dictionary containing only the requested companies."""
    missing = [company for company in companies if company not in prices_by_company]
    if missing:
        raise KeyError(f"Unknown companies: {', '.join(missing)}")
    return {company: prices_by_company[company] for company in companies}


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv_path", help="CSV with company, date, and close columns")
    parser.add_argument("companies", nargs="+", help="Company or ticker(s) to plot")
    args = parser.parse_args()
    prices_by_company, dates = read_prices(args.csv_path)
    try:
        chosen_prices = select_companies(prices_by_company, args.companies)
    except KeyError as error:
        parser.error(f"{error}. Available: {', '.join(prices_by_company)}")
    plot_prices(chosen_prices, dates)
    plt.show()

def keep_complete_dates(
    price_dict: dict[str, np.ndarray],
    time: np.ndarray,
) -> tuple[dict[str, np.ndarray], np.ndarray]:
    """Keep only dates where every company has a finite price.

    The returned dictionary and time array remain aligned. This is useful for
    portfolio calculations that require every held company to have a price on
    every simulated date.
    """
    if not price_dict:
        raise ValueError("Provide at least one company price array")

    time = np.asarray(time)
    price_arrays = [np.asarray(prices, dtype=float) for prices in price_dict.values()]
    if any(prices.ndim != 1 or len(prices) != len(time) for prices in price_arrays):
        raise ValueError("Every price array must be one-dimensional and match the time array length")

    price_matrix = np.vstack(price_arrays)
    valid_dates = np.isfinite(price_matrix).all(axis=0)

    clean_prices = {
        company: prices[valid_dates]
        for company, prices in price_dict.items()
    }
    clean_time = time[valid_dates]

    return clean_prices, clean_time
