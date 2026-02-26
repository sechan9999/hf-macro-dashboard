import numpy as np
import pandas as pd
from sklearn.mixture import GaussianMixture
from sklearn.preprocessing import StandardScaler

def fit_gmm_regimes(df_feat: pd.DataFrame, cols, n_regimes=3, min_train=120):
    """
    Expanding fit of GMM; outputs regime probabilities each month.
    """
    X = df_feat[cols].dropna().copy()
    idx = X.index

    scaler = StandardScaler()
    probs = pd.DataFrame(index=idx, columns=[f"pR{i}" for i in range(n_regimes)], dtype=float)
    labels = pd.Series(index=idx, dtype=float)

    for t in range(min_train, len(X)):
        train = X.iloc[:t]
        test = X.iloc[t:t+1]

        Z = scaler.fit_transform(train.values)
        gmm = GaussianMixture(n_components=n_regimes, covariance_type="full", random_state=7)
        gmm.fit(Z)

        zt = scaler.transform(test.values)
        pt = gmm.predict_proba(zt)[0]
        probs.iloc[t] = pt
        labels.iloc[t] = int(np.argmax(pt))

    out = probs.join(labels.rename("regime"))
    return out
