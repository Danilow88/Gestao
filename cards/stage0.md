# Stage 0 — Vibe Setup (Before/After)

**Time:** ≤5 min  
**Goal:** Launch the app and add a simple **Before/After** toggle so you can compare the baseline vs. a styled look. Keep it visual—no data logic yet.

---

## Setup (do once)

1) **Unzip the starter**
   - File: `finance-vibes-starter.zip`
   - Unzip anywhere, e.g. `~/projects/finance-vibes`

2) **Create & activate a virtual env**
   - macOS/Linux:
     ```bash
     cd ~/projects/finance-vibes
     python3 -m venv .venv
     source .venv/bin/activate
     ```
   - Windows (PowerShell):
     ```powershell
     cd ~/projects/finance-vibes
     python -m venv .venv
     .\.venv\Scripts\Activate.ps1
     ```

3) **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4) **Quick sanity**
   ```bash
   python -m pytest tests/ -v
   ```

5) **Run the app**
   ```bash
   streamlit run app/dashboard.py
   ```
   - If you see an import error, ensure you’re running from the repo root (`cd finance-vibes`).
   - If the default port is busy: `streamlit run app/dashboard.py --server.port 8502`

---

## Cursor Task (Paste)
> **Task:** In `app/dashboard.py`, add a sidebar toggle to compare **Before** vs **After** styles.  
> - Add: `preview = st.sidebar.radio("Preview", ["Before", "After"], index=0)`  
> - If **After**: inject a tiny CSS block and show a nicer title + subtitle.  
> - Always show two sidebar inputs: a date range and a channel multiselect (don’t wire them yet).  
> - Keep code minimal; the app must still run. Also, use the virtual environment created at .venv for all tasks.



---

## Optional drop-in snippet

> Place this **after** the line that loads data — i.e., after:  
> `df_tx, df_cust = load_data(DATA_DIR)`

```python
# --- Stage 0: Before/After toggle + basic sidebar ---
preview = st.sidebar.radio("Preview", ["Before", "After"], index=0)

# Always-on sidebar inputs (not wired yet)
date_min, date_max = df_tx["ts"].min().date(), df_tx["ts"].max().date()
st.sidebar.date_input("Date range", value=(date_min, date_max), key="date_range")
st.sidebar.multiselect(
    "Channels",
    options=sorted(df_tx["channel"].unique()),
    default=list(sorted(df_tx["channel"].unique())),
    key="channels_sel"
)

if preview == "After":
    st.markdown("""
        <style>
        .block-container { max-width: 1200px; padding-top: 1rem; }
        .fv-title { font-size: 1.8rem; font-weight: 700; }
        .fv-sub { color: rgba(0,0,0,.6); font-size: .95rem; margin-bottom: .75rem; }
        </style>
    """, unsafe_allow_html=True)
    st.markdown('<div class="fv-title">🏦 Finance Vibes</div>', unsafe_allow_html=True)
    st.markdown('<div class="fv-sub">Mini bank brain — visual edition</div>', unsafe_allow_html=True)
else:
    st.header("Finance Vibes (baseline)")
    st.caption("Plain look to compare against")
```

---

## Definition of Done
- App launches with no errors.
- Sidebar shows **Preview** toggle + date range + channel multiselect.
- Switching **Before/After** clearly changes the look (no data behavior changes yet).

## Stretch (optional)
- Add a theme toggle (light/dark).
- Footer showing “Last updated: <timestamp>”.
