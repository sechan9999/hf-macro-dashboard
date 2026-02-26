import numpy as np
import pandas as pd
from sklearn.covariance import LedoitWolf

def cov_shrink(rets_window: pd.DataFrame) -> np.ndarray:
    lw = LedoitWolf().fit(rets_window.values)
    return lw.covariance_

def vol_annual(cov: np.ndarray) -> np.ndarray:
    return np.sqrt(np.diag(cov)) * np.sqrt(12.0)
