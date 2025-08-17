from __future__ import annotations

from typing import Dict, Tuple
import numpy as np
import pandas as pd

def simulate(policy: Dict, df_txn: pd.DataFrame, df_cust: pd.DataFrame, n_boot: int = 200) -> Dict:
    """Run a tiny policy simulation with bootstrap CIs.

    Supported policies
    ------------------
    - {"type": "limit_uplift", "segment": "B", "pct": 0.10}
    - {"type": "fraud_threshold", "old": 0.7, "new": 0.6}
    - {"type": "rewards_tweak", "category": "groceries", "old": 0.01, "new": 0.02}

    Returns
    -------
    dict with delta_revenue, delta_risk, ci
    """
    # Baseline revenue approximation
    rev_base = (df_txn["amount"] * df_txn["fee_rate"] * (1 - df_txn["is_refund"])).sum()
    risk_base = df_txn["label_fraud"].mean()

    def revenue_under(policy):
        if policy.get("type") == "limit_uplift":
            seg = policy.get("segment", "B")
            pct = float(policy.get("pct", 0.1))
            affected = df_cust["risk_segment"] == seg
            uplift_factor = 1 + pct * affected.map({True:1, False:0})
            # join a crude per-customer spend proxy
            spend = df_txn.groupby("customer_id")["amount"].sum()
            joined = df_cust.join(spend, on="customer_id", how="left").fillna({"amount":0.0})
            new_spend = joined["amount"] * uplift_factor
            # revenue proportional to spend
            return float(new_spend.sum() * df_txn["fee_rate"].mean() * (1 - df_txn["is_refund"].mean()))
        if policy.get("type") == "rewards_tweak":
            cat = policy.get("category", "groceries")
            old = float(policy.get("old", 0.01))
            new = float(policy.get("new", 0.02))
            df = df_txn.copy()
            mask = df["category_hint"] == cat
            # Assume engagement lifts spend by 10% of reward delta on that category
            lift = 1 + 10 * (new - old)
            df.loc[mask, "amount"] = df.loc[mask, "amount"] * lift
            return float((df["amount"] * df["fee_rate"] * (1 - df["is_refund"])).sum())
        if policy.get("type") == "fraud_threshold":
            # revenue loss from blocking some good txns; assume 60% of txns above threshold are fraud
            old_t, new_t = float(policy.get("old", 0.7)), float(policy.get("new", 0.6))
            df = df_txn.copy()
            # imaginary scores ~ U(0,1) with fraud skew
            rng = np.random.default_rng(7)
            scores = rng.random(len(df)) * (0.6 + 0.8*df["label_fraud"])
            blocked_old = scores >= old_t
            blocked_new = scores >= new_t
            # block revenue for transactions that are NOT fraud
            good = df["label_fraud"] == 0
            rev_old = (df.loc[~blocked_old & good, "amount"] * df.loc[~blocked_old & good, "fee_rate"]).sum()
            rev_new = (df.loc[~blocked_new & good, "amount"] * df.loc[~blocked_new & good, "fee_rate"]).sum()
            return float(rev_new)
        return rev_base

    def risk_under(policy):
        if policy.get("type") == "limit_uplift":
            seg = policy.get("segment", "B")
            pct = float(policy.get("pct", 0.1))
            # More spend -> slight fraud exposure increase
            return float(risk_base * (1 + 0.2 * pct))
        if policy.get("type") == "rewards_tweak":
            # neutral risk
            return float(risk_base)
        if policy.get("type") == "fraud_threshold":
            old_t, new_t = float(policy.get("old", 0.7)), float(policy.get("new", 0.6))
            # Lower threshold => catch more fraud
            return float(max(0.0, risk_base - 0.05 * (new_t - old_t) / 0.1))
        return float(risk_base)

    # Point estimates
    rev_new = revenue_under(policy)
    risk_new = risk_under(policy)
    delta_revenue = float(rev_new - rev_base)
    delta_risk = float(risk_new - risk_base)

    # Bootstrap CI on revenue (risk assumed deterministic in this toy)
    rng = np.random.default_rng(11)
    boots = []
    idx = np.arange(len(df_txn))
    for _ in range(n_boot):
        samp = df_txn.iloc[rng.choice(idx, size=len(idx), replace=True)]
        boots.append(revenue_under(policy) - (samp["amount"] * samp["fee_rate"] * (1 - samp["is_refund"])).sum())
    lo, hi = np.percentile(boots, [5, 95]) if len(boots)>1 else (delta_revenue, delta_revenue)

    return {
        "policy": policy,
        "delta_revenue": delta_revenue,
        "delta_risk": delta_risk,
        "ci_90": [float(lo), float(hi)]
    }
