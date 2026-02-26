import os
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# -----------------------------
# Config
# -----------------------------
st.set_page_config(page_title="HF Multi-Factor Allocation Dashboard", layout="wide")

DEFAULT_PATHS = {
    "port_returns_csv": "data/out_port_returns.csv",
    "weights_csv": "data/out_weights.csv",
    "macro_parquet": "data/macro_equity_monthly.parquet",
    "exp_parquet": "data/exp_return_estimates_raw.parquet",     
    "regimes_parquet": "data/regimes.parquet",              
}

# -----------------------------
# Helpers
# -----------------------------
def read_csv_date_index(path: str, colname_guess=("date", "Date", "index")) -> pd.DataFrame:
    df = pd.read_csv(path)
    date_col = None
    for c in df.columns:
        if c in colname_guess:
            date_col = c
            break
    if date_col is None:
        date_col = df.columns[0]
    df[date_col] = pd.to_datetime(df[date_col])
    df = df.set_index(date_col).sort_index()
    return df

def max_drawdown_from_simple_returns(r: pd.Series) -> float:
    wealth = (1.0 + r).cumprod()
    dd = wealth / wealth.cummax() - 1.0
    return float(dd.min())

def ensure_datetime_index(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    if not isinstance(df.index, pd.DatetimeIndex):
        df.index = pd.to_datetime(df.index)
    return df.sort_index()

def load_optional_parquet(path: str) -> pd.DataFrame | None:
    if os.path.exists(path):
        try:
            df = pd.read_parquet(path)
            df = ensure_datetime_index(df)
            return df
        except Exception:
            return None
    return None

def last_non_nan(s: pd.Series):
    s2 = s.dropna()
    return s2.iloc[-1] if len(s2) else np.nan

# -----------------------------
# Load data
# -----------------------------
@st.cache_data
def load_all(paths):
    port = read_csv_date_index(paths["port_returns_csv"])
    if port.shape[1] == 1:
        port_col = port.columns[0]
    else:
        port_col = "port_ret" if "port_ret" in port.columns else port.select_dtypes(include=[np.number]).columns[0]
    port = port[[port_col]].rename(columns={port_col: "port_ret"})
    port = ensure_datetime_index(port)

    weights = read_csv_date_index(paths["weights_csv"])
    weights = ensure_datetime_index(weights)

    macro = pd.read_parquet(paths["macro_parquet"])
    macro = ensure_datetime_index(macro)

    exp = load_optional_parquet(paths["exp_parquet"])
    regimes = load_optional_parquet(paths["regimes_parquet"])

    return port, weights, macro, exp, regimes

try:
    port, weights, macro, exp, regimes = load_all(DEFAULT_PATHS)
except Exception as e:
    st.error(f"Failed to load data artifacts. Run `python run_backtest.py` first. Error: {e}")
    st.stop()

# Align a master index (monthly)
idx = port.index.intersection(weights.index).intersection(macro.index)
if exp is not None:
    idx = idx.intersection(exp.index)
if regimes is not None:
    idx = idx.intersection(regimes.index)

port = port.loc[idx]
weights = weights.loc[idx]
macro = macro.loc[idx]
if exp is not None:
    exp = exp.loc[idx]
if regimes is not None:
    regimes = regimes.loc[idx]

assets = list(weights.columns)

# -----------------------------
# Top KPIs
# -----------------------------
st.title("HF Multi-Factor Allocation Dashboard")

r = port["port_ret"]
ann_return = (1 + r).prod() ** (12 / max(len(r), 1)) - 1
ann_vol = r.std() * np.sqrt(12)
sharpe = ann_return / ann_vol if ann_vol > 0 else np.nan
mdd = max_drawdown_from_simple_returns(r)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Ann Return", f"{ann_return:.2%}")
c2.metric("Ann Vol", f"{ann_vol:.2%}")
c3.metric("Sharpe", f"{sharpe:.2f}" if np.isfinite(sharpe) else "NA")
c4.metric("Max Drawdown", f"{mdd:.2%}")

last_10y = last_non_nan(macro.get("dgs10", pd.Series(index=idx, dtype=float)))
last_3m = last_non_nan(macro.get("tb3ms", pd.Series(index=idx, dtype=float)))
last_cs = last_non_nan(macro.get("credit_spread", pd.Series(index=idx, dtype=float)))

m1, m2, m3 = st.columns(3)
if np.isfinite(last_10y): m1.metric("10Y yield (last)", f"{float(last_10y):.2f}%")
if np.isfinite(last_3m): m2.metric("3M rate (last)", f"{float(last_3m):.2f}%")
if np.isfinite(last_cs): m3.metric("Credit spread (last)", f"{float(last_cs)*100:.2f}%")

# -----------------------------
# Tabs
# -----------------------------
tab1, tab2, tab3 = st.tabs(["Performance & Allocation", "Macro Regimes", "Expected Asset Returns"])

with tab1:
    colA, colB = st.columns(2)
    with colA:
        wealth = (1 + port["port_ret"]).cumprod()
        fig = px.line(wealth.reset_index(), x=wealth.index.name or "index", y="port_ret", title="Cumulative Growth (Portfolio)")
        fig.update_layout(yaxis_title="Wealth (start=1)")
        st.plotly_chart(fig, use_container_width=True)

    with colB:
        figw = px.area(weights.reset_index(), x=weights.index.name or "index", y=assets, title="Portfolio Weights Over Time")
        st.plotly_chart(figw, use_container_width=True)

with tab2:
    if regimes is not None:
        pcols = [c for c in regimes.columns if c.startswith("pR")]
        current = regimes[pcols].iloc[-1]
        cols = st.columns(len(pcols))
        for i, pc in enumerate(pcols):
            cols[i].metric(pc, f"{current[pc]*100:.1f}%")
        fig = px.area(regimes.reset_index(), x=regimes.index.name or "index", y=pcols, title="Regime Probabilities Over Time (GMM)")
        st.plotly_chart(fig, use_container_width=True)

with tab3:
    if exp is not None:
        exp_cols = [c for c in exp.columns if c in assets]
        if exp_cols:
            fig = px.line(exp[exp_cols].reset_index(), x="index", y=exp_cols, title="Expected 12M Returns by Asset (Ridge Regression per Regime)")
            st.plotly_chart(fig, use_container_width=True)
