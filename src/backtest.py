import numpy as np
import pandas as pd
from .risk import cov_shrink
from .optimizer_cvar import optimize_cvar

def scenario_from_normal(mu, cov, n_scen=5000, seed=7):
    rng = np.random.default_rng(seed)
    # sample monthly *log* returns then convert to simple returns
    L = np.linalg.cholesky(cov)
    z = rng.standard_normal((n_scen, len(mu)))
    rlog = z @ L.T + mu  # log
    rsimple = np.expm1(rlog)
    return rsimple

def run_backtest(rets_log: pd.DataFrame, exp_log: pd.DataFrame,
                 lookback=60, start_idx=120,
                 lam=5.0, gamma=20.0, alpha=0.95,
                 bounds=None, cash_asset=None):
    assets = list(rets_log.columns)
    idx = rets_log.index.intersection(exp_log.index)

    rets_log = rets_log.loc[idx]
    exp_log = exp_log.loc[idx]

    w = np.array([1/len(assets)]*len(assets))
    w_hist = []
    port_ret = []

    for t in range(start_idx, len(idx)-1):
        dt = idx[t]
        # expected next 1m simple return
        mu_log = exp_log.iloc[t].values.astype(float)
        if np.any(np.isnan(mu_log)):
            mu_log = np.nan_to_num(mu_log, nan=0.0)
        mu_simple = np.expm1(mu_log)

        # risk (log return cov)
        win = rets_log.iloc[t-lookback:t]
        cov = cov_shrink(win)

        # scenarios of next month
        scen = scenario_from_normal(mu_log, cov, n_scen=1000, seed=7+t)

        # optimize
        w_new, _ = optimize_cvar(mu_simple, scen, w_prev=w, lam=lam, gamma=gamma, alpha=alpha,
                                 bounds=bounds, n_samples=5000, seed=7+t)

        # realize next month return
        r_next = np.expm1(rets_log.iloc[t+1].values)  # convert realized log to simple
        port_ret.append(float(r_next @ w_new))
        w_hist.append((dt, *w_new))

        w = w_new

    w_df = pd.DataFrame(w_hist, columns=["date"]+assets).set_index("date")
    port = pd.Series(port_ret, index=idx[start_idx+1: start_idx+1+len(port_ret)], name="port_ret")
    return port, w_df
