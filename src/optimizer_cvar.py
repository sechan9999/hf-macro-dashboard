import numpy as np

def cvar(losses: np.ndarray, alpha=0.95) -> float:
    # losses: (n_scenarios,)
    q = np.quantile(losses, alpha)
    tail = losses[losses >= q]
    return float(tail.mean()) if len(tail) else float(q)

def random_weights(n_assets, n_samples=50000, seed=7, bounds=None):
    rng = np.random.default_rng(seed)
    W = rng.random((n_samples, n_assets))
    W = W / W.sum(axis=1, keepdims=True)

    if bounds is not None:
        lo, hi = bounds  # arrays
        # simple projection-ish: clip then renormalize
        W = np.clip(W, lo, hi)
        W = W / W.sum(axis=1, keepdims=True)
    return W

def optimize_cvar(mu, scen_rets, w_prev, lam=5.0, gamma=20.0, alpha=0.95,
                  bounds=None, n_samples=60000, seed=7):
    """
    Objective: maximize  E[r] - lam*CVaR(loss) - gamma*turnover
    scen_rets: (n_scenarios, n_assets) in *simple returns* for next horizon (e.g. 1m)
    mu: (n_assets,) expected simple return next horizon
    """
    n_assets = len(mu)
    W = random_weights(n_assets, n_samples=n_samples, seed=seed, bounds=bounds)

    best = -1e18
    best_w = None
    for w in W:
        port = scen_rets @ w  # simple return scenarios
        losses = -port
        obj = float(mu @ w) - lam * cvar(losses, alpha=alpha) - gamma * float(np.abs(w - w_prev).sum())
        if obj > best:
            best = obj
            best_w = w
    return best_w, best
