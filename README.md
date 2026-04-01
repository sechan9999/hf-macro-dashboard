# ⚡ Macro Pulse: NVDA Danger Zone & Micro Footprint

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://hf-macro-dashboard.streamlit.app/)

A professional-grade financial dashboard designed for institutional-level macro analysis and real-time monitoring of NVDA (NVIDIA) market structure risks.

## 🔥 Key Feature: NVDA Danger Zone & Micro Footprint

The latest update adds a specialized panel for deep-dive analysis of NVDA, the engine of the AI revolution.

- **Composite Danger Index**: A real-time risk score (0 to 1) integrating RSI extension, ATR volatility, relative volume surges, VIX levels, and price distance from the 50-day SMA.
- **Micro Footprint Analysis**:
    - **Block Trade Detection**: Tracks institutional-sized volume spikes (>2× avg).
    - **Bid/Ask Imbalance Proxy**: Synthetic sentiment tracker measuring buyer dominance vs. seller supply.
    - **Volatility Spike Alert**: Visual markers for abnormal price swings.
- **Market Context**: Normalized performance comparison between NVDA and peers (SOXX, AMD, TSM, AVGO, MU).
- **Strategy Hint Cards**: Actionable trading guides based on the current risk zone (Safe/Caution/Danger).

## 🚀 Core Features

- **Institution-Grade Macro Dashboard**: Monitor S&P 500, 10Y Yields, Credit Spreads, and the Yield Curve.
- **Regime Classification**: GMM-modeled market states (Risk-On 🟢, Neutral 🟡, Risk-Off 🔴) to guide asset allocation.
- **Expected Return Model**: Predictive 12-month returns using expanding-window Ridge regression on macro features.
- **Monte Carlo Risk Sim**: Scenario testing with 5,000+ paths and VaR (Value at Risk) analysis.
- **✨ Gemini AI Analyst**: Built-in senior hedge fund analyst powered by Google Gemini 3 Flash to interpret data and provide rigorous investment briefings.

## 🛠 Tech Stack

- **Frontend**: [Streamlit](https://streamlit.io/)
- **Visualizations**: [Plotly](https://plotly.com/python/)
- **Data Source**: Live [Yahoo Finance](https://pypi.org/project/yfinance/) (no CSVs or FRED keys required for core functionality)
- **Machine Learning**: [Scikit-learn](https://scikit-learn.org/)
- **AI Engine**: [Google Gemini 3 Flash](https://aistudio.google.com/app/apikey) via Unified GenAI SDK

## 📋 Quick Start

### 1. Clone the repository
```bash
git clone https://github.com/sechan9999/NVDAmacropulse.git
cd NVDAmacropulse
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the app
```bash
streamlit run app.py
```

## 🧠 AI Integration

To activate the **Gemini AI Analyst**, simply enter your [Gemini API Key](https://aistudio.google.com/app/apikey) in the sidebar. The analyst will ingest live macro data and providing rigorous, data-driven briefings.

---
*© 2026 HF Research & Antigravity AI*
