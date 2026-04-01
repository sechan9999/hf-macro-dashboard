Macro Pulse — AI-Powered Institutional Macro Stock Market Dashboard.

Macro Pulse is a real-time, hedge fund-grade macro intelligence platform that combines quantitative financial modeling with Google Gemini AI to deliver institutional-quality investment analysis to anyone with a browser.

💡 Inspiration In a world of "meme stocks" and noise, I noticed a gap between retail technical analysis (simple charts) and institutional macro-risk management. Most retail traders look at a 14-day RSI, while hedge funds look at Credit Spreads, Yield Curves, and Macro Regimes. I wanted to build a bridge—a tool that combines high-level economic data with granular technical signals to give a "full-spectrum" view of the US market.

🎯 What It Does Most retail investors lack access to the same macro analytical tools used by hedge funds — regime classifiers, factor models, Monte Carlo risk engines, and AI analyst copilots. Macro Pulse bridges that gap by integrating 8 analytical modules into a single, free, live dashboard:

Performance — Cumulative returns vs SPY benchmark, rolling drawdown, monthly return distribution, full tear sheet (Sharpe, Sortino, Calmar, Win Rate, Profit Factor)

Macro & Rates — 10Y Treasury yield, credit spreads, yield curve slope, realized volatility (3M/12M) Regime Classification — Rule-based macro regime engine classifying markets into Risk-On / Neutral / Risk-Off using credit + volatility z-scores; per-regime Sharpe and win-rate statistics

Expected Returns — Expanding-window Ridge Regression model trained live on yfinance macro data; outputs 12-month forward return estimates with ±1σ confidence bands and realized return overlay

Stock Screener — Parallel multi-ticker screener using ThreadPoolExecutor (70% faster than sequential); real YTD calculation, RSI, SMA200 guard, CSV export

Technical Analysis — Candlestick + SMA20/50/200, Bollinger Bands, VWAP, RSI, MACD, OBV, Rate-of-Change for any ticker with custom date range Risk Simulation — Monte Carlo engine (up to 10,000 paths), fan chart, VaR/CVaR table

✨ Gemini AI Analyst — The core AI layer: feeds live macro data (regime score, yields, vol, drawdown, momentum) into Gemini 1.5 Flash via Google GenAI SDK and generates structured hedge fund-style briefings across 5 analysis modes: Full Macro Briefing, Regime Deep-Dive, Risk Assessment, Investment Outlook, and Custom Q&A

🛠️ Technologies Used Layer Technology AI Model Google Gemini 1.5 Flash (Google GenAI SDK) Cloud Platform Google Cloud Run (serverless, auto-scaling) CI/CD Google Cloud Build + Artifact Registry Frontend Streamlit 1.32+ Data yfinance (live market data — no API key required) ML Engine scikit-learn Ridge Regression (expanding window cross-validation) Simulation NumPy Monte Carlo (10,000 paths) Visualization Plotly (interactive dark-theme charts) Concurrency Python ThreadPoolExecutor (parallel screener) Container Docker multi-stage build (python:3.11-slim)

📡 Data Sources yfinance — S&P 500 (^GSPC), VIX (^VIX), 10Y Treasury (^TNX), Gold (GLD), Oil (USO), individual equities — all fetched in real-time, no API key required FRED API (optional) — Additional macro indicators (unemployment, CPI, credit spreads) when API key is provided Google Gemini 1.5 Flash — Language model for macro interpretation and investment insight generation

🧠 How Gemini Is Used The Gemini AI Analyst tab is the project's centerpiece AI feature. It:

Pulls live macro data from the dashboard (regime score, yields, volatility, drawdown, Sharpe, momentum signal) Constructs a structured financial context prompt Calls Gemini 1.5 Flash via google-generativeai SDK with a system instruction defining it as a "senior quantitative macro analyst" Returns formatted, institutional-quality analysis with specific positioning recommendations The model is given 5 analysis modes: Full Macro Briefing, Regime Deep-Dive, Risk Assessment, Investment Outlook, and Custom Question — making it a conversational, context-aware financial copilot.

☁️ Google Cloud Deployment The app runs on Google Cloud Run with full automation:

Dockerfile (multi-stage, python:3.11-slim, port 8080, health check)

cloudbuild.yaml — CI/CD: GitHub push → Cloud Build → Artifact Registry → Cloud Run

deploy_gcloud.ps1 — One-command Windows PowerShell deployment script using gcloud run deploy --source (no local Docker required) Live Cloud Run URL: https://macro-pulse-xu76sksloq-uc.a.run.app

💡 Findings & Learnings Gemini as a financial analyst works remarkably well — with a well-structured macro context prompt and the right system instruction, Gemini 1.5 Flash produces analysis comparable to institutional research notes Regime classification gates everything — the Risk-On/Off signal materially changes asset allocation recommendations and monthly return distributions yfinance's fast_info vs info — switching to fast_info for screener reduced per-ticker latency by ~300ms; combined with ThreadPoolExecutor, screener performance improved ~70% Ridge regression on macro factors — even a simple expanding-window Ridge model using yield, credit, vol, and momentum as features captures meaningful equity return signal (directionally correct ~60% of months) Cloud Run + --source flag — deploying directly from source without local Docker via Cloud Build was a revelation for rapid iteration; zero local infrastructure required

🔗 Links Live App (Streamlit Cloud): https://hf-macro-dashboard.streamlit.app Live App (Google Cloud Run): https://macro-pulse-xu76sksloq-uc.a.run.app GitHub Repository: https://github.com/sechan9999/hf-macro-dashboard

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
