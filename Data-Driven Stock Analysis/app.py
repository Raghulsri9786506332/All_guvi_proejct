"""Interactive Streamlit dashboard for annual Nifty 50 stock performance."""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import yaml

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from stock_analysis.analytics import calculate_metrics, monthly_leaders, sector_performance
from stock_analysis.pipeline import RAW_DIR, process_source, source_path

st.set_page_config(page_title="Data-Driven Stock Analysis", page_icon="📈", layout="wide")
st.title("📈 Data-Driven Stock Analysis")
st.caption("Explore market performance, volatility, monthly leaders, and return correlations.")


@st.cache_data(show_spinner="Validating stock data and preparing dashboard…")
def load_project_data(path: str, modified: float, sectors_modified: float):
    del modified, sectors_modified
    return process_source(path)


source = source_path()
if source is None or not source.is_file():
    st.info("Add the stock dataset YAML to get started.")
    st.markdown(
        f"""
        **No source dataset was provided with the project brief**, so this dashboard
        does not show fabricated prices or rankings.

        1. Place the monthly/date-wise YAML file in `{RAW_DIR}` as
           `stock_dataset.yaml` (or set `STOCK_DATA_PATH`).
        2. Add daily symbol, date, open, high, low, close, and volume fields.
        3. Optionally add `sectors.csv` with `symbol,sector` columns.
        4. Refresh this page.
        """
    )
    st.stop()

try:
    sectors_path = RAW_DIR / "sectors.csv"
    sectors_modified = sectors_path.stat().st_mtime if sectors_path.is_file() else 0.0
    raw_data, sector_data, report = load_project_data(
        str(source), source.stat().st_mtime, sectors_modified
    )
except (OSError, ValueError, pd.errors.ParserError, pd.errors.EmptyDataError, yaml.YAMLError) as error:
    st.error(f"Could not load the stock dataset: {error}")
    st.stop()

metrics = calculate_metrics(raw_data)
stock_summary = metrics["stocks"]
daily = metrics["daily"]
monthly = metrics["monthly"]
market = metrics["market"]
correlation = metrics["correlation"]

if stock_summary.empty:
    st.error("No valid daily prices remain after validation. Review the source file.")
    st.stop()

st.caption(
    f"Showing {int(market['stock_count'])} symbols through "
    f"{pd.Timestamp(market['latest_date']).date()} · "
    f"{report['accepted_rows']:,} valid observations"
)
if report["rejected_rows"] or report["duplicate_rows_removed"]:
    with st.expander("Data validation report"):
        st.write(
            f"Rejected rows: {report['rejected_rows']:,} · "
            f"Duplicate observations removed: {report['duplicate_rows_removed']:,}"
        )
        st.json(report["rejection_reasons"])

green = int(market["green_stocks"])
red = int(market["red_stocks"])
neutral = int(market["neutral_stocks"])
kpis = st.columns(5)
kpis[0].metric("Stocks analyzed", f"{int(market['stock_count']):,}")
kpis[1].metric("Green stocks", f"{green:,}", f"{green / int(market['stock_count']):.1%} of stocks")
kpis[2].metric("Red stocks", f"{red:,}", f"{red / int(market['stock_count']):.1%} of stocks")
kpis[3].metric("Avg. latest close", f"{market['average_latest_close']:,.2f}")
kpis[4].metric("Avg. latest volume", f"{market['average_latest_volume']:,.0f}")
if neutral:
    st.caption(f"{neutral} stock(s) had exactly zero annual return.")

st.subheader("Yearly performance")
left, right = st.columns(2)
with left:
    st.markdown("**Top 10 gainers**")
    gainers = stock_summary.nlargest(10, "annual_return_pct").sort_values("annual_return_pct")
    st.plotly_chart(
        px.bar(gainers, x="annual_return_pct", y="symbol", orientation="h",
               labels={"annual_return_pct": "Yearly return (%)", "symbol": "Symbol"},
               color="annual_return_pct", color_continuous_scale="Greens"),
        use_container_width=True,
    )
with right:
    st.markdown("**Top 10 losers**")
    losers = stock_summary.nsmallest(10, "annual_return_pct").sort_values("annual_return_pct", ascending=False)
    st.plotly_chart(
        px.bar(losers, x="annual_return_pct", y="symbol", orientation="h",
               labels={"annual_return_pct": "Yearly return (%)", "symbol": "Symbol"},
               color="annual_return_pct", color_continuous_scale="Reds_r"),
        use_container_width=True,
    )

st.subheader("Volatility and cumulative return")
volatile = stock_summary.nlargest(10, "volatility_pct").sort_values("volatility_pct")
st.plotly_chart(
    px.bar(volatile, x="volatility_pct", y="symbol", orientation="h",
           labels={"volatility_pct": "Annualized volatility (%)", "symbol": "Symbol"},
           color="volatility_pct", color_continuous_scale="Oranges"),
    use_container_width=True,
)
top_five = stock_summary.nlargest(5, "annual_return_pct")["symbol"].tolist()
top_daily = daily[daily["symbol"].isin(top_five)]
st.plotly_chart(
    px.line(top_daily, x="date", y="cumulative_return", color="symbol",
            labels={"date": "Date", "cumulative_return": "Cumulative return (%)", "symbol": "Symbol"},
            title="Cumulative return — top 5 yearly performers"),
    use_container_width=True,
)

st.subheader("Sector performance")
sectors = sector_performance(stock_summary, sector_data)
if sectors.empty:
    st.info("Add a `data/raw/sectors.csv` mapping with `symbol,sector` columns to enable this chart.")
else:
    st.plotly_chart(
        px.bar(sectors.sort_values("average_return_pct"),
               x="average_return_pct", y="sector", orientation="h",
               color="average_return_pct", color_continuous_scale="RdYlGn",
               labels={"average_return_pct": "Average yearly return (%)", "sector": "Sector"}),
        use_container_width=True,
    )

st.subheader("Stock return correlation")
if correlation.empty or correlation.shape[1] < 2:
    st.info("At least two stocks with overlapping observations are required for a correlation heatmap.")
else:
    st.plotly_chart(
        go.Figure(go.Heatmap(
            z=correlation.values,
            x=correlation.columns.tolist(),
            y=correlation.index.tolist(),
            zmin=-1,
            zmax=1,
            colorscale="RdBu",
            colorbar={"title": "Correlation"},
            hovertemplate="%{y} / %{x}<br>Correlation: %{z:.2f}<extra></extra>",
        )).update_layout(height=max(500, min(900, 20 * len(correlation) + 200))),
        use_container_width=True,
    )

st.subheader("Monthly top 5 gainers and losers")
available_months = sorted(pd.to_datetime(monthly["month"]).dropna().unique())
if not available_months:
    st.info("No monthly return observations are available.")
else:
    for start in range(0, len(available_months), 2):
        columns = st.columns(2)
        for offset, column in enumerate(columns):
            index = start + offset
            if index >= len(available_months):
                break
            month = pd.Timestamp(available_months[index])
            gainers_month, losers_month = monthly_leaders(monthly, month)
            with column:
                st.markdown(f"**{month.strftime('%B %Y')}**")
                chart_data = pd.concat(
                    [gainers_month.assign(result="Top gainers"),
                     losers_month.assign(result="Top losers")],
                    ignore_index=True,
                )
                st.plotly_chart(
                    px.bar(
                        chart_data,
                        x="symbol",
                        y="monthly_return_pct",
                        color="result",
                        barmode="group",
                        color_discrete_map={"Top gainers": "#16a34a", "Top losers": "#dc2626"},
                        labels={"symbol": "Symbol", "monthly_return_pct": "Monthly return (%)"},
                    ),
                    use_container_width=True,
                )

with st.expander("Stock summary table"):
    st.dataframe(
        stock_summary.style.format({
            "first_close": "{:,.2f}", "last_close": "{:,.2f}",
            "annual_return_pct": "{:+.2f}%", "volatility_pct": "{:.2f}%",
            "average_volume": "{:,.0f}",
        }),
        use_container_width=True,
        hide_index=True,
    )
st.caption("Historical data is not a guarantee of future performance. This dashboard is not investment advice.")
