# Stage 1 — Visual Explorer (10–15 min)

**Objective**  
Create a **hero visual** that responds to the sidebar filters, and add a one-line caption.

**Pick ONE hero:**  
1) **Donut** — spend share by `category_hint`  
2) **Timeline** — daily volume with weekend shading  
3) **Channel tiles** — KPI cards (card / pix / boleto) with tiny sparklines

**Instructions**  
- Use the **date range** + **channels** from the sidebar (Stage 0).  
- Show one crisp chart + a short caption explaining the most interesting thing.

**Definition of Done**  
- Filters change the chart immediately.  
- One-line caption updates with the filtered view.

---

## Option 1 — Donut (spend mix by category)

**Cursor prompt (paste):**  
> In `app/dashboard.py`, build a **Hero** section showing a Plotly donut of spend by `category_hint`.  
> - Read date range and channels from the sidebar (`st.session_state["date_range"]`, `st.session_state["channels_sel"]` if present; otherwise create them).  
> - Filter `df_tx` with those controls.  
> - Plot a donut (`px.pie(..., hole=0.5)`) and add a caption naming the **largest slice** and its value.  
> - Handle empty views gracefully (“No data in the current filter.”).  
> **Done:** Chart updates when filters change; caption names the largest slice.

```python
# --- Stage 1: filter + hero donut ---
import plotly.express as px

# Fallback: ensure we have controls if Stage 0 keys differ
date_min, date_max = df_tx["ts"].min().date(), df_tx["ts"].max().date()
date_range = st.session_state.get("date_range", (date_min, date_max))
channels_sel = st.session_state.get("channels_sel", sorted(df_tx["channel"].unique()))

# Filter
mask = (
    (df_tx["ts"].dt.date >= date_range[0]) &
    (df_tx["ts"].dt.date <= date_range[1]) &
    (df_tx["channel"].isin(channels_sel))
)
view = df_tx.loc[mask].copy()

# Hero donut
cat = view.groupby("category_hint", as_index=False)["amount"].sum().rename(columns={"amount":"total"})
fig = px.pie(cat, names="category_hint", values="total", hole=0.5)
st.subheader("Hero: Spend mix by category")
st.plotly_chart(fig, use_container_width=True)

# Caption
if not cat.empty:
    top = cat.sort_values("total", ascending=False).iloc[0]
    st.caption(f"Largest slice: **{top['category_hint']}** ({top['total']:.2f} in selected view).")
else:
    st.caption("No data in the current filter.")
```

---

## Option 2 — Timeline (daily volume, weekend shading)

**Cursor prompt (paste):**  
> In `app/dashboard.py`, create a **Daily volume timeline** that respects the sidebar filters.  
> - Resample `amount` by day and plot a line (`go.Scatter`).  
> - Add **weekend shading** using `add_vrect` for Sat/Sun.  
> - Caption should call out the **peak day** and its value.  
> **Done:** Line updates with filters; weekend shading visible; caption shows peak day.

```python
# --- Stage 1: timeline with weekend shading ---
import plotly.graph_objects as go
import pandas as pd

date_min, date_max = df_tx["ts"].min().date(), df_tx["ts"].max().date()
date_range = st.session_state.get("date_range", (date_min, date_max))
channels_sel = st.session_state.get("channels_sel", sorted(df_tx["channel"].unique()))

view = df_tx[
    (df_tx["ts"].dt.date >= date_range[0]) &
    (df_tx["ts"].dt.date <= date_range[1]) &
    (df_tx["channel"].isin(channels_sel))
].copy()

by_day = view.set_index("ts").resample("D")["amount"].sum().reset_index()

fig = go.Figure()
fig.add_trace(go.Scatter(x=by_day["ts"], y=by_day["amount"], mode="lines", name="Daily volume"))

# Weekend shading
if not by_day.empty:
    dmin, dmax = by_day["ts"].min().date(), by_day["ts"].max().date()
    rng = pd.date_range(dmin, dmax, freq="D")
    for d in rng:
        if d.weekday() >= 5:  # Sat/Sun
            fig.add_vrect(x0=d, x1=d + pd.Timedelta(days=1), fillcolor="LightGrey", opacity=0.15, line_width=0)

st.subheader("Hero: Daily volume")
st.plotly_chart(fig, use_container_width=True)

if len(by_day) > 0:
    hottest = by_day.iloc[by_day["amount"].idxmax()]
    st.caption(f"Peak day: **{hottest['ts'].date()}** with {hottest['amount']:.2f}.")
else:
    st.caption("No data in the current filter.")
```

---

## Option 3 — Channel tiles (KPIs + sparklines)

**Cursor prompt (paste):**  
> In `app/dashboard.py`, add **three KPI tiles** for channels (card, pix, boleto).  
> - Filter by sidebar controls.  
> - For each channel, show a `st.metric` with total amount and a tiny **sparkline** (`px.line` resampled daily).  
> - Caption should name the **largest channel** by total amount in view.  
> **Done:** Tiles + sparklines update when filters change; caption identifies the top channel.

```python
# --- Stage 1: channel KPI tiles with mini sparklines ---
import plotly.express as px

date_min, date_max = df_tx["ts"].min().date(), df_tx["ts"].max().date()
date_range = st.session_state.get("date_range", (date_min, date_max))
channels_sel = st.session_state.get("channels_sel", sorted(df_tx["channel"].unique()))

view = df_tx[
    (df_tx["ts"].dt.date >= date_range[0]) &
    (df_tx["ts"].dt.date <= date_range[1]) &
    (df_tx["channel"].isin(channels_sel))
].copy()

st.subheader("Hero: Channels at a glance")

cols = st.columns(3)
for i, ch in enumerate(["card", "pix", "boleto"]):
    sub = view[view["channel"] == ch].copy()
    kpi = sub["amount"].sum()
    with cols[i]:
        st.markdown(f"**{ch.capitalize()}**")
        st.metric("Total amount", f"{kpi:,.2f}")
        if not sub.empty:
            ts = sub.set_index("ts").resample("D")["amount"].sum().reset_index()
            fig = px.line(ts, x="ts", y="amount")
            fig.update_layout(height=140, margin=dict(l=10, r=10, t=10, b=10), showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.caption("No data")

# Caption
top_ch = (
    view.groupby("channel")["amount"].sum().sort_values(ascending=False)
    if not view.empty else None
)
if top_ch is not None and len(top_ch) > 0:
    st.caption(f"Largest channel: **{top_ch.index[0]}** ({top_ch.iloc[0]:.2f}).")
else:
    st.caption("No data in the current filter.")
```
