from __future__ import annotations

from pathlib import Path
from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd

from .ingest import load_data
from .categorize import Categorizer
from .risk import train_scorecard
from .experiment import simulate

app = FastAPI(title="Finance Vibes API")

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
categ = Categorizer(Path(__file__).resolve().parents[1] / "rules.yaml",
                    Path(__file__).resolve().parents[1] / "model.pkl")
df_tx, df_cust = load_data(DATA_DIR)

class CatReq(BaseModel):
    merchant: str
    amount: float

class ScoreReq(BaseModel):
    # For demo, accept a single-row payload
    amount: float
    installments: int = 1
    fee_rate: float = 0.01
    mcc: int = 5411
    channel: str = "card"
    country: str = "BR"

class PolicyReq(BaseModel):
    type: str
    segment: str | None = None
    pct: float | None = None
    old: float | None = None
    new: float | None = None
    category: str | None = None

@app.post("/categorize")
def categorize(req: CatReq):
    return {"category": categ.predict(req.merchant, req.amount)}

@app.post("/score")
def score(req: ScoreReq):
    model, report = train_scorecard(df_tx)
    proba = model.predict_proba(pd.DataFrame([req.dict()]))
    return {"p_default": float(proba[0]), "report": report}

@app.post("/simulate")
def simulate_policy(req: PolicyReq):
    out = simulate(req.dict(), df_tx, df_cust)
    return out
