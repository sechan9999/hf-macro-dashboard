import numpy as np
import pandas as pd

def add_macro_features(macro: pd.DataFrame) -> pd.DataFrame:
    df = macro.copy()

    df["cpi_yoy"] = np.log(df["cpi"]).diff(12)
    df["real10y_proxy"] = (df["dgs10"]/100.0) - df["cpi_yoy"]

    df["credit_spread"] = (df["baa"] - df["aaa"]) / 100.0
    df["yc_slope"] = df["t10y2y"] / 100.0
    df["rates_10y"] = df["dgs10"] / 100.0
    df["rates_3m"] = df["tb3ms"] / 100.0

    # growth proxies
    df["indpro_yoy"] = np.log(df["indpro"]).diff(12)
    df["unrate_chg_6m"] = df["unrate"].diff(6)

    # financial conditions (weekly -> monthly already)
    df["nfci_z"] = (df["nfci"] - df["nfci"].rolling(60).mean()) / df["nfci"].rolling(60).std()

    return df

def add_technical_features(rets: pd.DataFrame) -> pd.DataFrame:
    # ETF log returns monthly
    df = pd.DataFrame(index=rets.index)

    # momentum: 12-1 (classic)
    mom12 = rets.rolling(12).sum()
    mom1 = rets.rolling(1).sum()
    df["mom_12_1_spy"] = (mom12["SPY"] - mom1["SPY"])

    # realized vol
    df["rv_12_spy"] = rets["SPY"].rolling(12).std() * np.sqrt(12)

    # drawdown proxy on SPY
    cum = rets["SPY"].cumsum()
    peak = cum.cummax()
    df["dd_spy"] = (cum - peak)

    return df
