#!/usr/bin/env python3
"""
GCP BigQuery ETL Pipeline for Macro Pulse.

Extracts live macro and equity data, computes quantitative risk factors
and volatility-aware signals, and loads clean analytics marts into BigQuery.
"""

import sys
import os
import argparse
import datetime
import numpy as np
import pandas as pd
import yfinance as yf

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

# Ensure project root is in sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.bigquery_service import (
    save_macro_to_bigquery,
    save_quant_signals_to_bigquery,
    get_client,
    get_bq_status
)
from src.quant_signals import run_quant_scan

DEFAULT_WATCHLIST = [
    "SPY", "QQQ", "IWM", "NVDA", "AAPL", "MSFT", "AMZN",
    "GOOGL", "META", "TSLA", "SOXX", "TSM", "AVGO", "LLY",
    "COST", "JPM", "GLD", "USO", "TLT"
]


def extract_and_transform_macro() -> pd.DataFrame:
    """Extracts macro tickers and computes factor series."""
    print("📡 [ETL] Fetching macroeconomic time series...")
    tmap = {"sp500": "^GSPC", "vix": "^VIX", "dgs10": "^TNX", "gold": "GLD", "oil": "USO"}
    frames = {}
    for col, tkr in tmap.items():
        try:
            raw = yf.download(tkr, start="2005-01-01", auto_adjust=True, progress=False, multi_level_index=False)
            if not raw.empty:
                close = raw["Close"] if "Close" in raw.columns else raw.iloc[:, 0]
                close = close.dropna().resample("ME").last()
                close.index = close.index.to_period("M").to_timestamp()
                frames[col] = close
        except Exception as e:
            print(f"  Warning: Failed to load {tkr}: {e}")

    df = pd.DataFrame(frames).sort_index()
    df.index.name = "date"
    df["sp500_ret_m"] = np.log(df["sp500"]).diff()
    df["realized_vol_12m"] = df["sp500_ret_m"].rolling(12).std() * np.sqrt(12)
    df["realized_vol_3m"] = df["sp500_ret_m"].rolling(3).std() * np.sqrt(12)
    df["momentum_12_1"] = df["sp500_ret_m"].rolling(11).sum().shift(1)
    df["cumret"] = np.exp(df["sp500_ret_m"].cumsum()) * 100
    df["drawdown"] = df["cumret"] / df["cumret"].cummax() - 1
    df["dgs10"] = df["dgs10"].ffill()

    # Credit spread and yield curve slope proxy
    df["credit_spread"] = (df["dgs10"] * 0.35 + 1.5 - df["dgs10"] * 0.1).abs() / 100.0
    df["yc_slope"] = (df["dgs10"] - 3.5) / 100.0
    df["_credit_source"] = "proxy"
    df["_slope_source"] = "proxy"
    return df


def run_pipeline(project_id: str, dataset_id: str = "macropulse") -> None:
    """Executes the full extraction, transformation, and BigQuery load."""
    print("=" * 60)
    print(f"🚀 Launching Macro Pulse GCP Data Pipeline")
    print(f"   Target Project: {project_id}")
    print(f"   Target Dataset: {dataset_id}")
    print(f"   Timestamp:      {datetime.datetime.utcnow().isoformat()}Z")
    print("=" * 60)

    client, proj, ok = get_client(project_id)
    if not ok or client is None:
        print(f"❌ Failed to connect to GCP project {project_id}.")
        sys.exit(1)

    # 1. Macro Factors Mart
    macro_df = extract_and_transform_macro()
    print(f"✅ Processed {len(macro_df)} macro monthly records ({macro_df.index.min().strftime('%Y-%m')} to {macro_df.index.max().strftime('%Y-%m')}).")
    ok_macro = save_macro_to_bigquery(macro_df, project_id=project_id, dataset_id=dataset_id)
    if ok_macro:
        print(f"📦 [BigQuery] Successfully loaded -> `{project_id}.{dataset_id}.macro_factors`")
    else:
        print(f"❌ [BigQuery] Failed to load macro_factors table.")

    # 2. Quant Signals Mart
    print("\n⚡ [ETL] Running volatility-aware quant scan on universe...")
    scan_df = run_quant_scan(DEFAULT_WATCHLIST, period="1y")
    print(f"✅ Scanned {len(scan_df)} tickers.")

    # Clean column names for BigQuery
    signals_df = scan_df.rename(columns={
        "Ticker": "ticker",
        "Price": "price",
        "Signal": "signal",
        "Score": "score",
        "Vol Regime": "vol_regime",
        "Vol Breakout": "vol_breakout",
        "Reasons": "reasons",
        "_error": "error_message"
    })
    ok_signals = save_quant_signals_to_bigquery(signals_df, project_id=project_id, dataset_id=dataset_id)
    if ok_signals:
        print(f"📦 [BigQuery] Successfully loaded -> `{project_id}.{dataset_id}.quant_signals`")
    else:
        print(f"❌ [BigQuery] Failed to load quant_signals table.")

    print("\n📊 Verifying BigQuery dataset status...")
    status = get_bq_status(project_id=project_id, dataset_id=dataset_id)
    print(f"   Connected: {status['connected']}")
    print(f"   Tables in `{dataset_id}`: {status['tables']}")
    print("=" * 60)
    print("🎉 GCP BigQuery ETL Pipeline completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Macro Pulse GCP ETL Pipeline")
    parser.add_argument("--project", default="agentichackathon-506620", help="GCP Project ID")
    parser.add_argument("--dataset", default="macropulse", help="BigQuery Dataset ID")
    args = parser.parse_args()
    run_pipeline(project_id=args.project, dataset_id=args.dataset)
