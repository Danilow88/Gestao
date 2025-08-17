# Stage 2 — Interaction Candy (15–20 min)

**Objective**  
Make the app feel **alive** with micro-interactions and a tiny **Insight Pills** bar. Keep it visual-first (no heavy modeling).

**Pick ONE interaction:**  
1) **Cross-filter chips** — click/choose categories to filter the hero visual  
2) **Timeline zoom** — add a range/zoom control for the daily chart (visual brush)  
3) **Quick search** — highlight merchants matching a search box and show a small bar chart

**Also add:** an **Insight Pills** row that prints up to 3 short text bullets (largest category, peak day, and weekly trend).

**Definition of Done**  
- Interaction works (chips / zoom / search).  
- Pills update when the view changes.  
- No errors on rerun.

---

## Shared: helper to compute Insight Pills

```python
# --- Stage 2: Insight Pills helper ---
import pandas as pd

def compute_insight_pills(view: pd.DataFrame) -> list[str]:
    pills = []
    if view.empty:
        return ["No data in current view. Adjust filters."]
    # 1) Largest category by spend
    cat = view.groupby("category_hint")["amount"].sum().sort_values(ascending=False)
    if len(cat) > 0:
        pills.append(f"🍰 Largest category: **{cat.index[0]}** ({cat.iloc[0]:.2f}).")
    # 2) Peak day (by total amount)
    by_day = view.set_index("ts").resample("D")["amount"].sum()
    if len(by_day) > 0:
        mx_day = by_day.idxmax().date(); mx_val = by_day.max()
        pills.append(f"📅 Peak day: **{mx_day}** ({mx_val:.2f}).")
    # 3) Weekly trend vs previous week (simple diff on weekly sums)
    wk = view.set_index("ts").resample("W")["amount"].sum()
    if len(wk) >= 2:
        diff = wk.diff().dropna()
        trend = "up" if diff.iloc[-1] >= 0 else "down"
        pills.append(f"📈 Weekly trend: **{trend}** by {diff.iloc[-1]:.2f}.")
    return pills[:3]

def render_pills(pills: list[str]):
    cols = st.columns(min(3, len(pills)))
    for i, p in enumerate(pills):
        with cols[i]:
            st.info(p)
```

> Call `render_pills(compute_insight_pills(view))` after you compute your filtered `view` DataFrame (from Stage 1).

---

## Option 1 — Cross-filter chips (category)

**Cursor prompt (paste):**  
> In `app/dashboard.py`, add a **Category chips** multiselect that narrows the current view and updates the hero chart.  
> - Build `sel_cats = st.multiselect(..., options=sorted(df_tx["category_hint"].unique()), default=...)`.  
> - Filter `view` to `view2 = view[view["category_hint"].isin(sel_cats)]`.  
> - Re-render your hero (donut/tiles/timeline) using `view2`.  
> - Call `render_pills(compute_insight_pills(view2))`.  
> **Done:** Selecting chips changes the hero and pills.

```python
# --- Stage 2: Category chips cross-filter ---
cats = sorted(df_tx["category_hint"].unique())
sel_cats = st.multiselect("Category chips", options=cats, default=cats, help="Select one or more categories")

view2 = view[view["category_hint"].isin(sel_cats)].copy()

# Example: re-draw donut
import plotly.express as px
cat_mix = view2.groupby("category_hint", as_index=False)["amount"].sum().rename(columns={"amount":"total"})
fig = px.pie(cat_mix, names="category_hint", values="total", hole=0.5)
st.plotly_chart(fig, use_container_width=True)

render_pills(compute_insight_pills(view2))
```

---

## Option 2 — Timeline zoom (visual brush)

**Cursor prompt (paste):**  
> In `app/dashboard.py`, add **zoom controls** for the timeline.  
> - Compute `by_day` from the filtered view.  
> - Add `Zoom center` (`st.date_input`) and `Zoom window (days)` (`st.slider`).  
> - Compute `zoomed = by_day[(ts>=lo)&(ts<=hi)]` and show a caption with days shown.  
> - Enable a Plotly **rangeslider** on the x-axis.  
> - Keep pills based on the full filtered `view` (or `zoomed` if you prefer).  
> **Done:** Moving the controls changes the visible window; rangeslider appears.

```python
# --- Stage 2: Timeline zoom controls + rangeslider ---
import plotly.graph_objects as go
import pandas as pd

by_day = view.set_index("ts").resample("D")["amount"].sum().reset_index()

if not by_day.empty:
    dmin, dmax = by_day["ts"].min().date(), by_day["ts"].max().date()
    center = st.date_input("Zoom center", value=dmax)
    window = st.slider("Zoom window (days)", 7, 60, 21)
    lo = pd.to_datetime(center) - pd.Timedelta(days=window//2)
    hi = pd.to_datetime(center) + pd.Timedelta(days=window//2)
    zoomed = by_day[(by_day["ts"] >= lo) & (by_day["ts"] <= hi)]
else:
    zoomed = by_day.copy()

fig = go.Figure()
fig.add_trace(go.Scatter(x=by_day["ts"], y=by_day["amount"], mode="lines", name="Daily volume"))
fig.update_xaxes(rangeslider=dict(visible=True))

st.subheader("Timeline (with range slider)")
st.plotly_chart(fig, use_container_width=True)

st.caption(f"Zoomed window: {len(zoomed)} days shown.")
render_pills(compute_insight_pills(view))
```

---

## Option 3 — Quick search (merchant highlight + bar)

**Cursor prompt (paste):**  
> In `app/dashboard.py`, add a **Quick search** for merchants.  
> - Create `q = st.text_input("🔎 Quick search merchants", placeholder="Type part of a merchant name...")`.  
> - Filter the current `view` by `merchant.str.contains(q, case=False, na=False)`.  
> - Plot a **Top merchants** bar chart (top 10–12) and rotate x labels.  
> - Update the pills based on the searched subset.  
> **Done:** Typing narrows the chart and updates pills.

```python
# --- Stage 2: Merchant quick search ---
q = st.text_input("🔎 Quick search merchants", placeholder="Type part of a merchant name...")

sub = view.copy()
if q:
    mask = sub["merchant"].str.contains(q, case=False, na=False)
    sub = sub[mask]

# Top merchants bar
import plotly.express as px
top_merch = sub.groupby("merchant", as_index=False)["amount"].sum().sort_values("amount", ascending=False).head(12)

if not top_merch.empty:
    fig = px.bar(top_merch, x="merchant", y="amount")
    fig.update_layout(xaxis_tickangle=-30, margin=dict(l=10, r=10, t=10, b=60))
    st.plotly_chart(fig, use_container_width=True)
else:
    st.caption("No merchants match your search.")

render_pills(compute_insight_pills(sub))
```
