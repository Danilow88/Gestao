import pandas as pd
from app.risk import train_scorecard

def test_train_scorecard_minimal():
    # Small synthetic frame
    df = pd.DataFrame({
        "amount":[10,20,500,60,80,120],
        "installments":[1,1,3,2,1,6],
        "fee_rate":[0.01,0.01,0.015,0.01,0.01,0.02],
        "mcc":[5411,5812,6011,4111,5732,5999],
        "channel":["card","card","card","pix","card","boleto"],
        "country":["BR","BR","BR","BR","US","BR"],
        "label_fraud":[0,0,1,0,0,1],
        "income_band":["low","mid","mid","low","high","mid"]
    })
    model, report = train_scorecard(df, label="label_fraud")
    assert 0.0 <= report["metrics"]["auroc"] <= 1.0
    assert "features" in report["model"]
    assert isinstance(model.predict_proba(df), (list, tuple)) or model.predict_proba(df).shape[0] == len(df)
