"""Reusable market performance calculations for the dashboard and tests."""
from __future__ import annotations

import numpy as np
import pandas as pd

PRICE_COLUMNS = ("open", "high", "low", "close", "volume")
ANNUALIZATION_DAYS = 252


def _validated_prices(data: pd.DataFrame) -> pd.DataFrame:
    required = {"symbol", "date", "close", "volume"}
    missing = required - set(data.columns)
    if missing:
        raise ValueError(f"Missing required stock columns: {', '.join(sorted(missing))}")
    frame = data.copy()
    frame["symbol"] = frame["symbol"].astype(str).str.strip().str.upper()
    frame["date"] = pd.to_datetime(frame["date"], errors="coerce")
    frame["close"] = pd.to_numeric(frame["close"], errors="coerce")
    frame["volume"] = pd.to_numeric(frame["volume"], errors="coerce")
    frame = frame.dropna(subset=["symbol", "date", "close", "volume"])
    frame = frame.loc[frame["close"].gt(0) & frame["volume"].ge(0)]
    return frame.sort_values(["symbol", "date"]).drop_duplicates(["symbol", "date"], keep="last")


def calculate_metrics(data: pd.DataFrame) -> dict[str, pd.DataFrame | pd.Series]:
    """Calculate stock returns, volatility, market averages, and monthly returns."""
    prices = _validated_prices(data)
    if prices.empty:
        empty = pd.DataFrame()
        return {
            "daily": empty,
            "stocks": empty,
            "monthly": empty,
            "market": pd.Series(dtype=float),
            "correlation": empty,
        }

    prices["daily_return"] = prices.groupby("symbol", sort=False)["close"].pct_change()
    prices["cumulative_return"] = (
        (1 + prices["daily_return"].fillna(0))
        .groupby(prices["symbol"], sort=False)
        .cumprod() - 1
    ) * 100
    summary_rows = []
    for symbol, group in prices.groupby("symbol", sort=False):
        returns = group["daily_return"].dropna()
        summary_rows.append({
            "symbol": symbol,
            "first_date": group["date"].iloc[0],
            "last_date": group["date"].iloc[-1],
            "first_close": group["close"].iloc[0],
            "last_close": group["close"].iloc[-1],
            "annual_return_pct": (group["close"].iloc[-1] / group["close"].iloc[0] - 1) * 100,
            "volatility_pct": returns.std(ddof=1) * np.sqrt(ANNUALIZATION_DAYS) * 100
            if len(returns) > 1 else 0.0,
            "observations": len(group),
            "average_volume": group["volume"].mean(),
        })
    stocks = pd.DataFrame(summary_rows)

    latest = prices.sort_values("date").groupby("symbol", as_index=False, sort=False).tail(1)
    market = pd.Series({
        "stock_count": int(stocks["symbol"].nunique()),
        "green_stocks": int(stocks["annual_return_pct"].gt(0).sum()),
        "red_stocks": int(stocks["annual_return_pct"].lt(0).sum()),
        "neutral_stocks": int(stocks["annual_return_pct"].eq(0).sum()),
        "average_latest_close": float(latest["close"].mean()),
        "average_latest_volume": float(latest["volume"].mean()),
        "latest_date": latest["date"].max(),
    })

    prices["month"] = prices["date"].dt.to_period("M")
    monthly_rows = []
    for (month, symbol), group in prices.groupby(["month", "symbol"], sort=True):
        group = group.sort_values("date")
        monthly_rows.append({
            "month": month.to_timestamp(),
            "symbol": symbol,
            "first_close": group["close"].iloc[0],
            "last_close": group["close"].iloc[-1],
            "monthly_return_pct": (group["close"].iloc[-1] / group["close"].iloc[0] - 1) * 100,
        })
    monthly = pd.DataFrame(monthly_rows)

    close_wide = prices.pivot(index="date", columns="symbol", values="daily_return")
    correlation = close_wide.corr(min_periods=2)
    return {
        "daily": prices,
        "stocks": stocks.sort_values("annual_return_pct", ascending=False).reset_index(drop=True),
        "monthly": monthly,
        "market": market,
        "correlation": correlation,
    }


def sector_performance(stocks: pd.DataFrame, sectors: pd.DataFrame) -> pd.DataFrame:
    """Average annual return by mapped sector."""
    if stocks.empty or sectors.empty:
        return pd.DataFrame(columns=["sector", "average_return_pct", "stock_count"])
    merged = stocks.merge(sectors, on="symbol", how="inner")
    if merged.empty:
        return pd.DataFrame(columns=["sector", "average_return_pct", "stock_count"])
    return (
        merged.groupby("sector", as_index=False)
        .agg(average_return_pct=("annual_return_pct", "mean"), stock_count=("symbol", "nunique"))
        .sort_values("average_return_pct", ascending=False)
    )


def monthly_leaders(monthly: pd.DataFrame, month: pd.Timestamp, top_n: int = 5) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return top gainers and losers for one month."""
    selected = monthly.loc[pd.to_datetime(monthly["month"]).eq(pd.Timestamp(month))]
    ordered = selected.sort_values("monthly_return_pct", ascending=False)
    return ordered.head(top_n), ordered.tail(top_n).sort_values("monthly_return_pct")
