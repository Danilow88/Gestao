from __future__ import annotations

from pathlib import Path
from typing import Tuple
import pandas as pd

def load_data(data_dir: str | Path) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Load transactions and customers dataframes.

    Parameters
    ----------
    data_dir : str | Path
        Directory containing CSV files.

    Returns
    -------
    (df_tx, df_cust)
    """
    data_dir = Path(data_dir)
    df_tx = pd.read_csv(data_dir / "transactions_small.csv", parse_dates=["ts"])
    df_cust = pd.read_csv(data_dir / "customers_small.csv", parse_dates=["join_date"])
    return df_tx, df_cust

def basic_eda(df_tx: pd.DataFrame) -> pd.DataFrame:
    """Return a small summary table by channel and category hint."""
    g = df_tx.groupby(["channel", "category_hint"]).agg(
        n=("txn_id","count"),
        avg_amt=("amount","mean"),
        fraud_rate=("label_fraud","mean")
    ).reset_index()
    return g
