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
    price_column: str = "close",
    date_format: str = "%Y-%m-%d",
) -> dict[str, np.ndarray]:
    """Return company -> price array, sorted from oldest to newest.

    Each CSV row is one observation. Required default columns are company,
    date (YYYY-MM-DD), and close. Extra columns are ignored. Equal dates retain
    their CSV order. Indices count observations, not elapsed calendar days.
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

    # Sort chronologically, then collect one price array per company.
    data = data.sort_values(date_column, kind="stable")
    return {
        company: rows[price_column].to_numpy()
        for company, rows in data.groupby(company_column, sort=False)
    }


def plot_prices(
    prices_by_company: dict[str, np.ndarray],
    ax: Axes | None = None,
) -> Axes:
    """Plot every company price array in a dictionary on one chart."""
    plt.style.use('dark_background')
    if not prices_by_company:
        raise ValueError("Provide at least one company and price array")
    if ax is None:
        _, ax = plt.subplots(figsize=(10, 4), layout="constrained")
    for company, prices in prices_by_company.items():
        values = np.asarray(prices, dtype=float)
        if values.ndim != 1 or values.size == 0 or not np.isfinite(values).all():
            raise ValueError(f"{company!r} must have a nonempty, finite, one-dimensional price array")
        ax.plot(values, label=company, linewidth=1.8)
    ax.set(title="Stock prices", xlabel="Observation index (oldest → newest)", ylabel="Price")
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
    prices_by_company = read_prices(args.csv_path)
    try:
        chosen_prices = select_companies(prices_by_company, args.companies)
    except KeyError as error:
        parser.error(f"{error}. Available: {', '.join(prices_by_company)}")
    plot_prices(chosen_prices)
    plt.show()

