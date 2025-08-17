# Finance Vibes – Mini Bank Brain

Fast, friendly coding session in Cursor. Build a tiny consumer-finance brain in 5 stages:
1) Explore → 2) Feature → 3) Risk → 4) Decision → 5) Ship

## Quickstart

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Run tests
python -m pytest tests/ -v

# Streamlit dashboard
streamlit run app/dashboard.py


# FastAPI
uvicorn app.api:app --reload
```

## Data
Synthetic, safe samples live in `data/`:
- `transactions_small.csv`: 1.2k rows of card/pix/boleto transactions
- `customers_small.csv`: 120 customers with income and risk segment info

## Modules
- `app/ingest.py`: load & EDA helpers
- `app/categorize.py`: `Categorizer` with YAML rules and optional ML fallback
- `app/risk.py`: tiny scorecard-style model (no sklearn needed)
- `app/experiment.py`: bootstrap policy simulation
- `app/api.py`: `/categorize`, `/score`, `/simulate`
- `app/dashboard.py`: 3-tab Streamlit UI

## Prompts to paste in Cursor
- Refactor functions to pure, add type hints & docstrings with examples.
- Write pytest for edge cases (NaNs, zero amounts, unseen merchants).
- Explain the model to an exec in 5 bullets.
- Generate an executive summary of decisions with a table of tradeoffs.
- Suggest 3 fairness checks across `income_band` and `country`.

## License
MIT (starter template)
