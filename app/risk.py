from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Tuple
import numpy as np
import pandas as pd

@dataclass
class ScorecardModel:
    features: list
    bins: Dict[str, np.ndarray]
    coefs: Dict[str, float]
    intercept: float

    def predict_proba(self, df: pd.DataFrame) -> np.ndarray:
        x = np.zeros(len(df))
        for f in self.features:
            val = df[f].to_numpy()
            # Simple monotonic transform: log(1+x)
            if np.issubdtype(val.dtype, np.number):
                v = np.log1p(np.maximum(0.0, val))
            else:
                # one-hot by category order hash
                v = pd.Categorical(val).codes.astype(float)
            x += self.coefs.get(f, 0.0) * v
        logits = self.intercept + x
        # sigmoid
        return 1.0 / (1.0 + np.exp(-logits))

def auroc(y_true: np.ndarray, y_score: np.ndarray) -> float:
    # Simple AUC implementation (no sklearn)
    order = np.argsort(y_score)
    y = np.array(y_true)[order]
    n_pos = y.sum()
    n_neg = len(y) - n_pos
    if n_pos == 0 or n_neg == 0:
        return 0.5
    cum_neg = 0
    rank_sum = 0.0
    for i in range(len(y)):
        if y[i] == 1:
            rank_sum += cum_neg
        else:
            cum_neg += 1
    return rank_sum / (n_pos * n_neg)

def train_scorecard(df: pd.DataFrame, label: str = "label_fraud") -> Tuple[ScorecardModel, Dict]:
    """Train a tiny, explainable score (no external deps).

    Uses a few interpretable transforms and returns a model and a plaintext-ish report.
    """
    # Select up to 6 simple features
    candidate = ["amount", "installments", "fee_rate", "mcc", "channel", "country"]
    feat = [f for f in candidate if f in df.columns][:6]
    # Coefs: hand-weighted by quick correlation proxy
    coefs = {}
    for f in feat:
        s = df[f]
        if s.dtype.kind in "biufc":
            coefs[f] = float(np.sign(np.corrcoef(np.nan_to_num(s), df[label])[0,1]) * 0.3)
        else:
            coefs[f] = 0.1
    intercept = -2.0
    model = ScorecardModel(features=feat, bins={}, coefs=coefs, intercept=intercept)
    p = model.predict_proba(df)
    auc = auroc(df[label].to_numpy(), p)
    # KS
    # simple KS: max diff between positive and negative cdfs
    pos = np.sort(p[df[label]==1])
    neg = np.sort(p[df[label]==0])
    def cdf(x, arr):
        return (arr <= x).mean() if len(arr)>0 else 0.5
    grid = np.linspace(0,1,101)
    ks = float(max(abs(cdf(g,pos)-cdf(g,neg)) for g in grid))

    # Top drivers (by abs coef)
    top = sorted(coefs.items(), key=lambda kv: abs(kv[1]), reverse=True)[:3]
    drivers = [f"{k} ({'+' if v>=0 else '-'} impact)" for k,v in top]

    # Fairness check across income_band if present
    fairness = {}
    if "income_band" in df.columns:
        by_band = []
        for band, grp in df.groupby("income_band"):
            if len(grp) >= 10:
                auc_b = auroc(grp[label].to_numpy(), model.predict_proba(grp))
                by_band.append((band, float(auc_b), float(grp[label].mean())))
        fairness["income_band"] = [{"band":b, "auroc":a, "positive_rate":pr} for b,a,pr in by_band]

    report = {
        "model": {
            "features": feat,
            "coefs": coefs,
            "intercept": intercept
        },
        "metrics": {
            "auroc": float(auc),
            "ks": float(ks)
        },
        "explanation": {
            "top_drivers": drivers,
            "notes": "Simple monotonic transforms; coefficients scaled by correlation sign."
        },
        "fairness": fairness
    }
    return model, report
