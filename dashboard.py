# ============================================================
#  5D BIM Construction Dashboard  –  Dark Neon Fitness Theme
# ============================================================
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from supabase import create_client
import os
from datetime import datetime, timedelta
import io
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

# ===== CONFIGURATION =====
SUPABASE_URL = st.secrets["supabase_url"] if "supabase_url" in st.secrets else os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = st.secrets["supabase_key"] if "supabase_key" in st.secrets else os.environ.get("SUPABASE_KEY", "")
# =========================

st.set_page_config(
    page_title="5D BIM Dashboard",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ============================  MASTER CSS  ============================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700;1,9..40,300&family=JetBrains+Mono:wght@400;500;600&display=swap');

*{box-sizing:border-box;margin:0;padding:0;}

html,body,.stApp{
  background:#090b0f !important;
  font-family:'DM Sans',sans-serif;
  color:#dce8ff;
}

/* wipe default chrome */
header[data-testid="stHeader"]{display:none!important;}
#MainMenu,footer,.stDeployButton{display:none!important;}
div[data-testid="stToolbar"]{display:none!important;}
div[data-testid="stDecoration"]{display:none!important;}

.block-container{
  padding:1rem 1.4rem 2rem !important;
  max-width:100%!important;
}

/* ── CARDS ─────────────────────────────────────────────── */
.card{
  background:#111622;
  border:1px solid rgba(255,255,255,0.06);
  border-radius:22px;
  padding:1.15rem 1.2rem;
  position:relative;
  overflow:hidden;
  height:100%;
}
.card-gradient{
  background:linear-gradient(145deg,#2a1765 0%,#6b1878 48%,#c42760 100%);
  border-radius:22px;
  padding:1.15rem 1.2rem;
  position:relative;
  overflow:hidden;
  height:100%;
}
.card-gradient::after{
  content:'';
  position:absolute;
  top:-40px;right:-40px;
  width:160px;height:160px;
  background:radial-gradient(circle,rgba(255,80,200,.35) 0%,transparent 70%);
  pointer-events:none;
}
.card-dark{
  background:#0d101a;
  border:1px solid rgba(255,255,255,0.05);
  border-radius:22px;
  padding:1.15rem 1.2rem;
  position:relative;
  overflow:hidden;
  height:100%;
}

/* ── TYPOGRAPHY ─────────────────────────────────────────── */
.label{
  color:#5a6a8a;
  font-size:.84rem;
  text-transform:uppercase;
  letter-spacing:1.6px;
  font-weight:500;
  margin-bottom:1px;
}
.big-val{
  color:#eef4ff;
  font-size:2.5rem;
  font-weight:700;
  font-family:'JetBrains Mono',monospace;
  line-height:1.05;
}
.med-val{
  color:#eef4ff;
  font-size:1.5rem;
  font-weight:600;
  font-family:'JetBrains Mono',monospace;
  line-height:1.1;
}
.sm-val{
  color:#eef4ff;
  font-size:1.1rem;
  font-weight:600;
  font-family:'JetBrains Mono',monospace;
}
.sub{
  color:rgba(255,255,255,.4);
  font-size:.72rem;
  font-weight:400;
  margin-left:3px;
}
.section-header{
  color:#eef4ff;
  font-size:.9rem;
  font-weight:700;
  text-transform:uppercase;
  letter-spacing:2px;
  margin-bottom:.9rem;
  opacity:.7;
}
.brand{
  position:absolute;
  bottom:.9rem;right:1.1rem;
  font-size:.58rem;
  color:rgba(255,255,255,.18);
  text-transform:uppercase;
  letter-spacing:2.5px;
  font-weight:600;
}

/* ── BADGES ─────────────────────────────────────────────── */
.badge{
  display:inline-block;
  padding:2px 9px;
  border-radius:20px;
  font-size:.75rem;
  font-weight:700;
  letter-spacing:.6px;
  text-transform:uppercase;
}
.bg{background:rgba(0,255,136,.13);color:#00ff88;border:1px solid rgba(0,255,136,.3);}
.br{background:rgba(255,70,70,.13);color:#ff6b6b;border:1px solid rgba(255,70,70,.3);}
.ba{background:rgba(255,183,0,.13);color:#ffb700;border:1px solid rgba(255,183,0,.3);}
.bb{background:rgba(0,160,255,.13);color:#00aaff;border:1px solid rgba(0,160,255,.3);}

/* ── MINI BAR CHART ─────────────────────────────────────── */
.mini-bars{
  display:flex;
  align-items:flex-end;
  gap:5px;
  height:52px;
  margin-top:.65rem;
}
.mb{
  flex:1;
  border-radius:5px 5px 0 0;
  min-height:4px;
}
.mb-green{background:#00ff88;}
.mb-pink{background:#ff3d9a;}
.mb-dim{background:#1a2535;}
.day-row{
  display:flex;
  gap:5px;
  margin-top:5px;
}
.day-row span{
  flex:1;
  text-align:center;
  font-size:.53rem;
  color:#374454;
  text-transform:uppercase;
}

/* ── KPI ROW (icon + value) ─────────────────────────────── */
.kpi-row{
  display:flex;
  align-items:center;
  gap:.5rem;
  padding:.4rem 0;
  border-bottom:1px solid rgba(255,255,255,.04);
}
.kpi-row:last-child{border-bottom:none;}
.kpi-icon{font-size:1.1rem;width:22px;text-align:center;}
.kpi-text{flex:1;}
.kpi-label{font-size:.78rem;color:#5a6a8a;text-transform:uppercase;letter-spacing:1px;}
.kpi-val{font-size:1.1rem;font-weight:600;color:#eef4ff;font-family:'JetBrains Mono',monospace;}
.kpi-badge{margin-left:auto;}

/* ── PROGRESS BAR ─────────────────────────────────────────── */
.pbar-wrap{
  background:rgba(255,255,255,.07);
  border-radius:999px;
  height:5px;
  margin-top:4px;
  overflow:hidden;
}
.pbar-fill{
  height:100%;
  border-radius:999px;
  background:linear-gradient(90deg,#00ff88,#00e0cc);
}
.pbar-fill-pink{
  height:100%;
  border-radius:999px;
  background:linear-gradient(90deg,#ff3d9a,#ff8c42);
}

/* ── DIVIDER ─────────────────────────────────────────────── */
.div{
  height:1px;
  background:linear-gradient(90deg,transparent,rgba(255,255,255,.08),transparent);
  margin:.9rem 0;
}

/* ── STREAMLIT COMPONENT OVERRIDES ─────────────────────── */
.stSelectbox label,.stMultiSelect label,.stSlider label,.stNumberInput label{
  color:#5a6a8a!important;font-size:.72rem!important;text-transform:uppercase;letter-spacing:1px;
}
div[data-baseweb="select"]>div{
  background:#0d101a!important;
  border-color:rgba(255,255,255,.1)!important;
  border-radius:12px!important;
  color:#eef4ff!important;
}
.stButton>button{
  background:linear-gradient(135deg,#131d33,#0d1422);
  border:1px solid rgba(0,160,255,.25);
  border-radius:40px;
  color:#6ab4ff;
  font-family:'DM Sans',sans-serif;
  font-size:.78rem;
  font-weight:500;
  width:100%;
  padding:.45rem 1rem;
  transition:all .2s;
}
.stButton>button:hover{
  border-color:#00aaff;
  box-shadow:0 0 14px rgba(0,160,255,.3);
  color:#aad6ff;
}
h1,h2,h3{color:#c5deff!important;font-weight:600;}
.stDataFrame{border-radius:16px!important;overflow:hidden;}
div[data-testid="stMetric"]{display:none!important;}

/* ── EXPANDER ────────────────────────────────────────────── */
div[data-testid="stExpander"]{
  background:#0d101a;
  border:1px solid rgba(255,255,255,.06);
  border-radius:16px;
  padding:.2rem .4rem;
}
div[data-testid="stExpander"] summary{color:#6a8ab0!important;}

/* ── PLOTLY CHART BORDER ─────────────────────────────────── */
div[data-testid="stPlotlyChart"]{
  border-radius:18px;
  overflow:hidden;
}

/* ── ALERT / WARNING ─────────────────────────────────────── */
div[data-testid="stAlert"]{
  border-radius:14px!important;
  background:#0d101a!important;
}

/* ── SCROLLBAR ─────────────────────────────────────────── */
::-webkit-scrollbar{width:4px;height:4px;}
::-webkit-scrollbar-track{background:#090b0f;}
::-webkit-scrollbar-thumb{background:#1e2d4a;border-radius:4px;}

/* ── DASHBOARD HEADER ─────────────────────────────────────── */
.dash-header{
  display:flex;
  justify-content:space-between;
  align-items:flex-start;
  margin-bottom:1.2rem;
}
.dash-title{font-size:1.6rem;font-weight:700;color:#eef4ff;letter-spacing:-.3px;}
.dash-sub{font-size:.7rem;color:#3a4a62;margin-top:3px;}
.dash-time{font-size:.68rem;color:#3a4a62;font-family:'JetBrains Mono',monospace;text-align:right;}
</style>
""", unsafe_allow_html=True)


# ============================  PLOTLY THEME  ============================
DARK_BG   = "rgba(0,0,0,0)"
GRID_CLR  = "rgba(255,255,255,0.05)"
TEXT_CLR  = "#5a6a8a"
GREEN     = "#00ff88"
PINK      = "#ff3d9a"
BLUE      = "#00aaff"
AMBER     = "#ffb700"
PURPLE    = "#a855f7"

def dark_fig(fig):
    fig.update_layout(
        paper_bgcolor=DARK_BG,
        plot_bgcolor=DARK_BG,
        font=dict(family="DM Sans", color=TEXT_CLR, size=11),
        margin=dict(l=10, r=10, t=30, b=10),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            font=dict(color="#6a8ab0", size=10),
        ),
    )
    fig.update_xaxes(
        gridcolor=GRID_CLR, showgrid=False,
        linecolor=GRID_CLR, tickfont=dict(color=TEXT_CLR, size=10),
    )
    fig.update_yaxes(
        gridcolor=GRID_CLR, showgrid=True,
        linecolor="rgba(0,0,0,0)",
        tickfont=dict(color=TEXT_CLR, size=10),
    )
    return fig


# ============================  SUPABASE  ============================
@st.cache_resource
def init_supabase():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = init_supabase()

@st.cache_data(ttl=60)
def load_projects():
    return pd.DataFrame(supabase.table("projects").select("*").execute().data)

@st.cache_data(ttl=60)
def load_elements(pid):
    return pd.DataFrame(
        supabase.table("elements").select("*")
        .eq("project_id", pid).eq("is_primary", True).execute().data
    )

@st.cache_data(ttl=60)
def load_schedule(pid):
    return pd.DataFrame(
        supabase.table("schedule_tasks").select("*").eq("project_id", pid).execute().data
    )

@st.cache_data(ttl=60)
def load_comments(pid):
    return pd.DataFrame(
        supabase.table("comments").select("*")
        .eq("project_id", pid).order("created_at", desc=True).execute().data
    )

@st.cache_data(ttl=60)
def load_photos(pid):
    return pd.DataFrame(
        supabase.table("photos").select("*")
        .eq("project_id", pid).order("uploaded_at", desc=True).execute().data
    )

@st.cache_data(ttl=60)
def load_spi_history(pid):
    return pd.DataFrame(
        supabase.table("spi_history").select("*")
        .eq("project_id", pid).order("recorded_at", desc=True).execute().data
    )


# ============================  LOAD DATA  ============================
projects_df = load_projects()
if projects_df.empty:
    st.warning("No projects found.")
    st.stop()

project_names = projects_df["name"].tolist()
selected_project = st.sidebar.selectbox("🏢 Project", project_names)
project_id = projects_df[projects_df["name"] == selected_project]["id"].iloc[0]

elements_df   = load_elements(project_id)
schedule_df   = load_schedule(project_id)
comments_df   = load_comments(project_id)
photos_df     = load_photos(project_id)
spi_history_df = load_spi_history(project_id)

if elements_df.empty or schedule_df.empty:
    st.warning("No data. Run sync tool first.")
    st.stop()

# ---- Merge & compute ----
merged = pd.merge(elements_df, schedule_df, on="task_id", how="inner")
merged["SPI"]        = merged["earned_value"] / merged["planned_value"]
merged["CPI"]        = merged["earned_value"] / merged["actual_cost"]
merged["Delayed"]    = merged["SPI"] < 1.0
merged["OverBudget"] = merged["CPI"] < 1.0

# ============================  SIDEBAR CONTROLS  ============================
st.sidebar.markdown("## ⚙️ Controls")
extra_cost = st.sidebar.number_input("Extra Cost (KES)", value=0, step=1000)

proj_res     = supabase.table("projects").select("extra_cost").eq("id", project_id).execute()
current_extra = proj_res.data[0]["extra_cost"] if proj_res.data else 0
if extra_cost != current_extra:
    supabase.table("projects").update({"extra_cost": extra_cost}).eq("id", project_id).execute()
    st.sidebar.success("Extra cost updated")

# ============================  FILTER STATE (session_state — widgets live at bottom) ============================
_all_cats   = list(merged["category"].unique())
_status_all = ["On Track", "Delayed", "Over Budget", "Delayed & Over"]
_spi_min    = float(merged["SPI"].min()); _spi_max = float(merged["SPI"].max())
_cpi_min    = float(merged["CPI"].min()); _cpi_max = float(merged["CPI"].max())
if _spi_min == _spi_max: _spi_min -= 0.1; _spi_max += 0.1
if _cpi_min == _cpi_max: _cpi_min -= 0.1; _cpi_max += 0.1

if "f_cats"   not in st.session_state: st.session_state["f_cats"]   = _all_cats
if "f_status" not in st.session_state: st.session_state["f_status"] = _status_all
if "f_spi"    not in st.session_state: st.session_state["f_spi"]    = (_spi_min, _spi_max)
if "f_cpi"    not in st.session_state: st.session_state["f_cpi"]    = (_cpi_min, _cpi_max)

categories    = st.session_state["f_cats"]
status_filter = st.session_state["f_status"]
spi_low, spi_high = st.session_state["f_spi"]
cpi_low, cpi_high = st.session_state["f_cpi"]

status_conditions = []
if "On Track"       in status_filter: status_conditions.append((~merged["Delayed"]) & (~merged["OverBudget"]))
if "Delayed"        in status_filter: status_conditions.append(merged["Delayed"] & (~merged["OverBudget"]))
if "Over Budget"    in status_filter: status_conditions.append((~merged["Delayed"]) & merged["OverBudget"])
if "Delayed & Over" in status_filter: status_conditions.append(merged["Delayed"] & merged["OverBudget"])
final_status = status_conditions[0] if status_conditions else pd.Series([True] * len(merged))
for cond in status_conditions[1:]: final_status |= cond

filtered = merged[
    (merged["category"].isin(categories)) &
    (final_status) &
    (merged["SPI"].between(spi_low, spi_high)) &
    (merged["CPI"].between(cpi_low, cpi_high))
]

# ---- Helper functions (defined here; expanders rendered at bottom) ----
def recalc_costs():
    count = 0
    for _, elem in elements_df.iterrows():
        map_res  = supabase.table("quantity_mapping").select("quantity_type").eq("category", elem.get("category","")).execute()
        if not map_res.data: continue
        qty_type = map_res.data[0]["quantity_type"]
        quantity = {"Volume": elem.get("volume",0),"Area": elem.get("area",0),
                    "Length": elem.get("length",0),"Count": elem.get("count",1)}.get(qty_type, 1) or 1
        unit_cost = elem.get("unit_cost",0) or 0
        supabase.table("elements").update({"total_cost": quantity*unit_cost}).eq("id", elem["id"]).execute()
        count += 1
    return count

def update_progress_from_photos():
    photos = supabase.table("photos").select("task_id","completion_status","uploaded_at").eq("project_id", project_id).execute()
    if not photos.data: return 0
    latest = {}
    for p in photos.data:
        tid = p["task_id"]
        if not tid: continue
        if tid not in latest or p["uploaded_at"] > latest[tid]["uploaded_at"]:
            latest[tid] = p
    count = 0
    for tid, info in latest.items():
        pct = {"Not Started":0,"In Progress":50,"Complete":100}.get(info.get("completion_status","Not Started"), 0)
        supabase.table("schedule_tasks").update({"percent_complete": pct}).eq("project_id", project_id).eq("task_id", tid).execute()
        count += 1
    return count


# ============================  COMPUTE KPIs  ============================
total_pv = filtered["planned_value"].sum()
total_ev = filtered["earned_value"].sum()
total_ac = filtered["actual_cost"].sum()

overall_spi      = total_ev / total_pv if total_pv else 1.0
overall_cpi      = total_ev / total_ac if total_ac else 1.0
overall_progress = (filtered["percent_complete"] * filtered["planned_value"]).sum() / total_pv if total_pv else 0
total_length     = filtered["length"].sum() if "length" in filtered.columns else 0
num_elements     = len(filtered)
num_categories   = filtered["category"].nunique()
delayed_count    = filtered["Delayed"].sum()
overbudget_count = filtered["OverBudget"].sum()
on_track         = num_elements - int(delayed_count) - int(overbudget_count)

variance_cost  = total_ev - total_ac
variance_sched = total_ev - total_pv

today_str  = datetime.now().strftime("%b %d, %Y")
clock_str  = datetime.now().strftime("%H:%M")

# ── Generate weekly synthetic bar data (7 days, based on category SPI distribution)
cats       = filtered["category"].unique()[:7]
weekly_spis = [max(0.2, min(1.0, filtered[filtered["category"]==c]["SPI"].mean())) if c in filtered["category"].values else 0.3 for c in cats]
while len(weekly_spis) < 7: weekly_spis.append(0)
weekly_spis = weekly_spis[:7]
max_spi    = max(weekly_spis) if max(weekly_spis) > 0 else 1
bar_pcts   = [v / max_spi for v in weekly_spis]
DAYS       = ["S","M","T","W","T","F","S"]

def badge(val, lo=0.95, hi=1.0):
    if val >= hi: return f'<span class="badge bg">On Track</span>'
    if val >= lo: return f'<span class="badge ba">Warning</span>'
    return f'<span class="badge br">Behind</span>'

def badge_cpi(val):
    if val >= 1.0: return f'<span class="badge bg">Under Budget</span>'
    if val >= 0.9: return f'<span class="badge ba">Warning</span>'
    return f'<span class="badge br">Over Budget</span>'

def progress_bar(pct, pink=False):
    cls = "pbar-fill-pink" if pink else "pbar-fill"
    return f'<div class="pbar-wrap"><div class="{cls}" style="width:{pct*100:.1f}%"></div></div>'

def mini_bars_html(heights, days=DAYS):
    bars = ""
    for i, h in enumerate(heights):
        today_idx = datetime.now().weekday() % 7
        cls = "mb-green" if i < today_idx else ("mb-pink" if i == today_idx else "mb-dim")
        bars += f'<div class="mb {cls}" style="height:{max(6, int(h*52))}px"></div>'
    day_spans = "".join(f"<span>{d}</span>" for d in days)
    return f'<div class="mini-bars">{bars}</div><div class="day-row">{day_spans}</div>'


# ============================  DASHBOARD HEADER  ============================
st.markdown(f"""
<div class="dash-header">
  <div>
    <div class="dash-title">🏗️ {selected_project}</div>
    <div class="dash-sub">5D BIM · Construction Performance Dashboard</div>
  </div>
  <div class="dash-time">
    {clock_str}<br>{today_str}
  </div>
</div>
""", unsafe_allow_html=True)


# ============================  ROW 1 — OVERVIEW CARDS  ============================
c1, c2, c3 = st.columns([1, 1, 1], gap="small")

# ── Card 1: "This Week" (week-summary + mini bar chart)
with c1:
    prog_pct = overall_progress * 100
    st.markdown(f"""
    <div class="card glow-green" style="box-shadow:0 0 22px rgba(0,255,136,0.08)">
      <div class="section-header">This Week</div>
      <div style="display:flex;justify-content:space-between;align-items:flex-start">
        <div>
          <div class="label">Progress</div>
          <div class="big-val">{prog_pct:.1f}<span class="sub">%</span></div>
        </div>
        <div style="text-align:right">
          <div class="label">Tasks</div>
          <div class="med-val">{on_track}<span class="sub">/{num_elements}</span></div>
          <div style="margin-top:4px"><span class="badge bg">on track</span></div>
        </div>
      </div>
      {mini_bars_html(bar_pcts)}
      <div class="brand">BIM</div>
    </div>
    """, unsafe_allow_html=True)

# ── Card 2: "Today" — 3 inline KPI rows
with c2:
    ev_disp  = f"{total_ev/1e6:.2f}M" if total_ev >= 1e6 else f"{total_ev:,.0f}"
    pv_disp  = f"{total_pv/1e6:.2f}M" if total_pv >= 1e6 else f"{total_pv:,.0f}"
    ac_disp  = f"{total_ac/1e6:.2f}M" if total_ac >= 1e6 else f"{total_ac:,.0f}"
    st.markdown(f"""
    <div class="card" style="box-shadow:0 0 22px rgba(0,160,255,0.07)">
      <div class="section-header">Today</div>
      <div class="kpi-row">
        <div class="kpi-icon">📐</div>
        <div class="kpi-text">
          <div class="kpi-label">Earned Value</div>
          <div class="kpi-val">{ev_disp} KES</div>
        </div>
        <div class="kpi-badge">{badge(overall_spi)}</div>
      </div>
      <div class="kpi-row">
        <div class="kpi-icon">📋</div>
        <div class="kpi-text">
          <div class="kpi-label">Planned Value</div>
          <div class="kpi-val">{pv_disp} KES</div>
        </div>
        <div class="kpi-badge"><span class="badge bb">planned</span></div>
      </div>
      <div class="kpi-row">
        <div class="kpi-icon">🔥</div>
        <div class="kpi-text">
          <div class="kpi-label">Actual Cost</div>
          <div class="kpi-val">{ac_disp} KES</div>
        </div>
        <div class="kpi-badge">{badge_cpi(overall_cpi)}</div>
      </div>
      <div class="brand">BIM</div>
    </div>
    """, unsafe_allow_html=True)

# ── Card 3: SPI / CPI gauges (small bar-style)
with c3:
    spi_pct = min(overall_spi, 1.5) / 1.5
    cpi_pct = min(overall_cpi, 1.5) / 1.5
    spi_col = "#00ff88" if overall_spi >= 0.95 else ("#ffb700" if overall_spi >= 0.8 else "#ff6b6b")
    cpi_col = "#00ff88" if overall_cpi >= 1.0 else ("#ffb700" if overall_cpi >= 0.9 else "#ff6b6b")
    st.markdown(f"""
    <div class="card-dark" style="box-shadow:0 0 22px rgba(168,85,247,0.1)">
      <div class="section-header">Performance</div>
      <div style="margin-bottom:1rem">
        <div style="display:flex;justify-content:space-between;align-items:baseline">
          <div class="label">Schedule Performance</div>
          <div class="sm-val" style="color:{spi_col}">{overall_spi:.3f}</div>
        </div>
        <div class="pbar-wrap" style="margin-top:6px">
          <div style="height:100%;border-radius:999px;width:{spi_pct*100:.1f}%;background:{spi_col};transition:width .5s"></div>
        </div>
      </div>
      <div style="margin-bottom:1rem">
        <div style="display:flex;justify-content:space-between;align-items:baseline">
          <div class="label">Cost Performance</div>
          <div class="sm-val" style="color:{cpi_col}">{overall_cpi:.3f}</div>
        </div>
        <div class="pbar-wrap" style="margin-top:6px">
          <div style="height:100%;border-radius:999px;width:{cpi_pct*100:.1f}%;background:{cpi_col};transition:width .5s"></div>
        </div>
      </div>
      <div style="display:flex;gap:.5rem;flex-wrap:wrap">
        <span class="badge {'bg' if overall_spi>=0.95 else 'br'}">{delayed_count} delayed</span>
        <span class="badge {'bg' if overall_cpi>=1.0 else 'br'}">{overbudget_count} over budget</span>
      </div>
      <div class="brand">BIM</div>
    </div>
    """, unsafe_allow_html=True)


st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

# ============================  ROW 2 — GRADIENT CARD + DONUT  ============================
col_left, col_right = st.columns([3, 2], gap="small")

# ── Left: Large gradient KPI card (purple→pink like image)
with col_left:
    vcost_disp   = f"+{variance_cost/1e3:.0f}K" if variance_cost >= 0 else f"{variance_cost/1e3:.0f}K"
    vsched_disp  = f"+{variance_sched/1e3:.0f}K" if variance_sched >= 0 else f"{variance_sched/1e3:.0f}K"
    vcost_col    = "#00ff88" if variance_cost >= 0 else "#ff6b6b"
    vsched_col   = "#00ff88" if variance_sched >= 0 else "#ff6b6b"
    total_length_disp = f"{total_length:,.1f}" if total_length else "—"

    st.markdown(f"""
    <div class="card-gradient">
      <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:1rem;margin-bottom:1rem">
        <div>
          <div class="label" style="color:rgba(255,255,255,.5)">Planned Value</div>
          <div class="med-val">{total_pv/1e6:.2f}M</div>
          <div style="font-size:.6rem;color:rgba(255,255,255,.35)">KES</div>
        </div>
        <div>
          <div class="label" style="color:rgba(255,255,255,.5)">Earned Value</div>
          <div class="med-val">{total_ev/1e6:.2f}M</div>
          <div style="font-size:.6rem;color:rgba(255,255,255,.35)">KES</div>
        </div>
        <div>
          <div class="label" style="color:rgba(255,255,255,.5)">Actual Cost</div>
          <div class="med-val">{total_ac/1e6:.2f}M</div>
          <div style="font-size:.6rem;color:rgba(255,255,255,.35)">KES</div>
        </div>
      </div>
      <div class="div" style="background:rgba(255,255,255,.12)"></div>
      <div style="display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:.8rem">
        <div>
          <div class="label" style="color:rgba(255,255,255,.45)">SPI</div>
          <div class="sm-val">{overall_spi:.3f}</div>
        </div>
        <div>
          <div class="label" style="color:rgba(255,255,255,.45)">CPI</div>
          <div class="sm-val">{overall_cpi:.3f}</div>
        </div>
        <div>
          <div class="label" style="color:rgba(255,255,255,.45)">Cost Var</div>
          <div class="sm-val" style="color:{vcost_col}">{vcost_disp}</div>
        </div>
        <div>
          <div class="label" style="color:rgba(255,255,255,.45)">Sched Var</div>
          <div class="sm-val" style="color:{vsched_col}">{vsched_disp}</div>
        </div>
      </div>
      <div class="div" style="background:rgba(255,255,255,.12)"></div>
      <div style="display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:.8rem">
        <div>
          <div class="label" style="color:rgba(255,255,255,.45)">Elements</div>
          <div class="sm-val">{num_elements}</div>
        </div>
        <div>
          <div class="label" style="color:rgba(255,255,255,.45)">Categories</div>
          <div class="sm-val">{num_categories}</div>
        </div>
        <div>
          <div class="label" style="color:rgba(255,255,255,.45)">Length</div>
          <div class="sm-val">{total_length_disp} m</div>
        </div>
        <div>
          <div class="label" style="color:rgba(255,255,255,.45)">Extra Cost</div>
          <div class="sm-val">{extra_cost:,.0f}</div>
        </div>
      </div>
      <div class="brand" style="color:rgba(255,255,255,.2)">BIM</div>
    </div>
    """, unsafe_allow_html=True)

# ── Right: Donut ring (multi-color, like the fitness app)
with col_right:
    cat_ev = filtered.groupby("category")["earned_value"].sum().reset_index()
    ring_colors = ["#00aaff","#ff3d9a","#00ff88","#ffb700","#a855f7","#ff8c42","#00e0cc"]

    fig_donut = go.Figure(go.Pie(
        labels=cat_ev["category"],
        values=cat_ev["earned_value"],
        hole=0.62,
        marker=dict(colors=ring_colors[:len(cat_ev)], line=dict(color="#090b0f", width=3)),
        textinfo="none",
        hovertemplate="<b>%{label}</b><br>EV: %{value:,.0f}<extra></extra>",
    ))
    fig_donut.add_annotation(
        text=f"<b>{overall_progress*100:.0f}%</b><br><span style='font-size:9px'>Done</span>",
        x=0.5, y=0.5, showarrow=False, font=dict(size=18, color="#eef4ff"), align="center",
    )
    fig_donut.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        showlegend=True,
        legend=dict(
            bgcolor="rgba(0,0,0,0)", font=dict(color="#5a6a8a", size=9),
            orientation="v", x=1, y=0.5,
        ),
        margin=dict(l=0, r=80, t=10, b=10),
        height=220,
    )
    st.markdown('<div class="card-dark" style="padding:.8rem;box-shadow:0 0 22px rgba(168,85,247,0.1)">'
                '<div class="section-header">EV by Category</div>', unsafe_allow_html=True)
    st.plotly_chart(fig_donut, use_container_width=True, config={"displayModeBar": False})
    st.markdown("</div>", unsafe_allow_html=True)


st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

# ============================  ROW 3 — BAR CHARTS  ============================
bc1, bc2 = st.columns([1, 1], gap="small")

with bc1:
    cat_summary = filtered.groupby("category").agg({"planned_value": "sum", "actual_cost": "sum"}).reset_index()
    fig_bar = go.Figure()
    fig_bar.add_trace(go.Bar(
        name="Planned", x=cat_summary["category"], y=cat_summary["planned_value"],
        marker_color=BLUE, marker_line_width=0, opacity=0.85,
    ))
    fig_bar.add_trace(go.Bar(
        name="Actual Cost", x=cat_summary["category"], y=cat_summary["actual_cost"],
        marker_color=GREEN, marker_line_width=0, opacity=0.85,
    ))
    fig_bar.update_layout(
        barmode="group", title="Planned vs Actual Cost",
        title_font=dict(color="#8aa2c0", size=12),
        height=260,
    )
    dark_fig(fig_bar)
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.plotly_chart(fig_bar, use_container_width=True, config={"displayModeBar": False})
    st.markdown("</div>", unsafe_allow_html=True)

with bc2:
    cat_spi = filtered.groupby("category").agg({"SPI": "mean", "CPI": "mean"}).reset_index()
    fig_spi = go.Figure()
    fig_spi.add_trace(go.Bar(
        name="SPI", x=cat_spi["category"], y=cat_spi["SPI"],
        marker_color=PINK, marker_line_width=0, opacity=0.9,
    ))
    fig_spi.add_trace(go.Bar(
        name="CPI", x=cat_spi["category"], y=cat_spi["CPI"],
        marker_color=AMBER, marker_line_width=0, opacity=0.9,
    ))
    fig_spi.add_hline(y=1.0, line_dash="dot", line_color=GREEN, line_width=1,
                      annotation_text="Target 1.0", annotation_font_color=GREEN, annotation_font_size=9)
    fig_spi.update_layout(
        barmode="group", title="SPI & CPI by Category",
        title_font=dict(color="#8aa2c0", size=12), height=260,
    )
    dark_fig(fig_spi)
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.plotly_chart(fig_spi, use_container_width=True, config={"displayModeBar": False})
    st.markdown("</div>", unsafe_allow_html=True)


st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

# ============================  ROW 4 — COST BREAKDOWN + DELAY WARNING  ============================
r4c1, r4c2 = st.columns([1, 1], gap="small")

with r4c1:
    cost_by_cat = filtered.groupby("category")["total_cost"].sum().reset_index()
    fig_pie = go.Figure(go.Pie(
        labels=cost_by_cat["category"], values=cost_by_cat["total_cost"],
        hole=0.5,
        marker=dict(colors=ring_colors[:len(cost_by_cat)], line=dict(color="#090b0f", width=2)),
        textinfo="percent",
        textfont=dict(size=9, color="#eef4ff"),
        hovertemplate="<b>%{label}</b><br>%{value:,.0f} KES<extra></extra>",
    ))
    fig_pie.update_layout(
        title="Cost Breakdown by Category",
        title_font=dict(color="#8aa2c0", size=12),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        height=280,
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#5a6a8a", size=9)),
        margin=dict(l=0, r=10, t=35, b=0),
    )
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.plotly_chart(fig_pie, use_container_width=True, config={"displayModeBar": False})
    st.markdown("</div>", unsafe_allow_html=True)

with r4c2:
    st.markdown('<div class="card" style="height:100%">', unsafe_allow_html=True)
    st.markdown('<div class="section-header">🔮 Delay Intelligence</div>', unsafe_allow_html=True)

    if not spi_history_df.empty:
        spi_history_df["recorded_at"] = pd.to_datetime(spi_history_df["recorded_at"])
        spi_trend = (spi_history_df
                     .sort_values(["task_id","recorded_at"], ascending=[True, False])
                     .groupby("task_id").head(3))
        decreasing = []
        for tid, grp in spi_trend.groupby("task_id"):
            if len(grp) >= 3:
                spis = grp.sort_values("recorded_at")["spi"].values
                if spis[0] > spis[1] > spis[2]:
                    decreasing.append(tid)
        if decreasing:
            st.markdown(f"""
            <div style="background:rgba(255,107,107,.07);border:1px solid rgba(255,107,107,.2);border-radius:14px;padding:.8rem 1rem;margin-bottom:.6rem">
              <div style="color:#ff6b6b;font-size:.75rem;font-weight:600">⚠️ SPI Declining</div>
              <div style="color:#e2eaff;font-size:.72rem;margin-top:.3rem">{", ".join(decreasing)}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="background:rgba(0,255,136,.07);border:1px solid rgba(0,255,136,.2);border-radius:14px;padding:.8rem 1rem">
              <div style="color:#00ff88;font-size:.75rem;font-weight:600">✅ No Negative Trends</div>
              <div style="color:#5a6a8a;font-size:.72rem;margin-top:.3rem">All SPI trends are stable or improving</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="color:#5a6a8a;font-size:.72rem;padding:.5rem 0">
          Run sync tool 3+ times to enable trend analysis
        </div>
        """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="div"></div>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:.7rem">
      <div style="background:rgba(255,107,107,.07);border:1px solid rgba(255,107,107,.15);border-radius:12px;padding:.7rem">
        <div class="label">Delayed Tasks</div>
        <div class="med-val" style="color:#ff6b6b">{int(delayed_count)}</div>
      </div>
      <div style="background:rgba(255,183,0,.07);border:1px solid rgba(255,183,0,.15);border-radius:12px;padding:.7rem">
        <div class="label">Over Budget</div>
        <div class="med-val" style="color:#ffb700">{int(overbudget_count)}</div>
      </div>
      <div style="background:rgba(0,255,136,.07);border:1px solid rgba(0,255,136,.15);border-radius:12px;padding:.7rem">
        <div class="label">On Track</div>
        <div class="med-val" style="color:#00ff88">{on_track}</div>
      </div>
      <div style="background:rgba(0,160,255,.07);border:1px solid rgba(0,160,255,.15);border-radius:12px;padding:.7rem">
        <div class="label">Categories</div>
        <div class="med-val" style="color:#00aaff">{num_categories}</div>
      </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

# ============================  ROW 5 — RISK HEATMAP  ============================
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown('<div class="section-header">⚠️ Risk Heatmap</div>', unsafe_allow_html=True)

heat_cols = ["task_id","category","SPI","CPI","Delayed","OverBudget"]
heat_df   = filtered[heat_cols].copy()
heat_df["SPI"] = heat_df["SPI"].map("{:.3f}".format)
heat_df["CPI"] = heat_df["CPI"].map("{:.3f}".format)

def color_risk(val):
    try:
        v = float(val)
        if v < 0.8:  return "background-color:#3d0f0f;color:#ff6b6b"
        if v < 0.95: return "background-color:#3d2e0f;color:#ffb700"
        return "background-color:#0f2e1a;color:#00ff88"
    except:
        return ""

styled_heat = heat_df.style.map(color_risk, subset=["SPI","CPI"])
st.dataframe(styled_heat, use_container_width=True, height=280)
st.markdown("</div>", unsafe_allow_html=True)


st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

# ============================  ROW 6 — MONTE CARLO  ============================
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown('<div class="section-header">🎲 Monte Carlo Simulation</div>', unsafe_allow_html=True)

mc_c1, mc_c2 = st.columns([3, 1], gap="small")
with mc_c1:
    num_sim  = st.slider("Simulations", 100, 2000, 500, step=100)
    spi_vals = filtered["SPI"].dropna()
    if len(spi_vals) > 0:
        sim_spi = np.random.choice(spi_vals, size=(num_sim, max(len(spi_vals),1)), replace=True)
        sim_dur = 100 / sim_spi.mean(axis=1)
        fig_mc  = px.histogram(
            sim_dur, nbins=50,
            color_discrete_sequence=[BLUE],
            opacity=0.8,
        )
        fig_mc.add_vline(x=100, line_dash="dot", line_color=GREEN, line_width=1.5,
                         annotation_text="Baseline 100d", annotation_font_color=GREEN, annotation_font_size=9)
        fig_mc.add_vline(x=np.percentile(sim_dur,80), line_dash="dash", line_color=PINK, line_width=1.5,
                         annotation_text=f"P80={np.percentile(sim_dur,80):.0f}d",
                         annotation_font_color=PINK, annotation_font_size=9)
        fig_mc.update_layout(
            title="Simulated Project Duration (days)",
            title_font=dict(color="#8aa2c0", size=12),
            showlegend=False, height=220,
            xaxis_title="Duration (days)", yaxis_title="Frequency",
        )
        dark_fig(fig_mc)
        st.plotly_chart(fig_mc, use_container_width=True, config={"displayModeBar": False})

with mc_c2:
    if len(spi_vals) > 0:
        p50 = np.percentile(sim_dur, 50)
        p80 = np.percentile(sim_dur, 80)
        p90 = np.percentile(sim_dur, 90)
        st.markdown(f"""
        <div style="display:flex;flex-direction:column;gap:.6rem;padding-top:.5rem">
          <div style="background:rgba(0,255,136,.08);border:1px solid rgba(0,255,136,.2);border-radius:12px;padding:.7rem">
            <div class="label">P50 Duration</div>
            <div class="med-val" style="color:#00ff88">{p50:.0f}<span class="sub">days</span></div>
          </div>
          <div style="background:rgba(255,61,154,.08);border:1px solid rgba(255,61,154,.2);border-radius:12px;padding:.7rem">
            <div class="label">P80 Duration</div>
            <div class="med-val" style="color:#ff3d9a">{p80:.0f}<span class="sub">days</span></div>
          </div>
          <div style="background:rgba(255,183,0,.08);border:1px solid rgba(255,183,0,.2);border-radius:12px;padding:.7rem">
            <div class="label">P90 Duration</div>
            <div class="med-val" style="color:#ffb700">{p90:.0f}<span class="sub">days</span></div>
          </div>
        </div>
        """, unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)


st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

# ============================  ROW 7 — PHOTOS + COMMENTS  ============================
ph_col, cm_col = st.columns([1, 1], gap="small")

with ph_col:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-header">📸 Site Photos</div>', unsafe_allow_html=True)
    if not photos_df.empty:
        for _, row in photos_df.iterrows():
            st.image(row["file_path"], caption=row.get("caption",""), use_column_width=True)
            if row.get("task_id"):
                prog = schedule_df[schedule_df["task_id"] == row["task_id"]]["percent_complete"].values
                pv   = prog[0] / 100 if len(prog) else 0
                st.markdown(f"""
                <div style="margin-bottom:.5rem">
                  <div style="font-size:.65rem;color:#5a6a8a;margin-bottom:3px">Task {row['task_id']} – {pv*100:.0f}% complete</div>
                  {progress_bar(pv)}
                </div>
                """, unsafe_allow_html=True)
    else:
        st.markdown('<div style="color:#3a4a62;font-size:.75rem;padding:.5rem 0">No site photos uploaded yet.</div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with cm_col:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-header">💬 Comments</div>', unsafe_allow_html=True)

    for _, row in comments_df.iterrows():
        if row.get("is_emergency"):
            st.markdown(f"""
            <div style="background:rgba(255,60,60,.08);border-left:3px solid #ff6b6b;border-radius:0 10px 10px 0;padding:.5rem .75rem;margin-bottom:.5rem">
              <div style="color:#ff6b6b;font-size:.65rem;font-weight:600">🚨 {row['user_name']}</div>
              <div style="color:#e2eaff;font-size:.72rem;margin-top:2px">{row['comment']}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="background:rgba(255,255,255,.03);border-left:3px solid #1e3050;border-radius:0 10px 10px 0;padding:.5rem .75rem;margin-bottom:.5rem">
              <div style="color:#6ab4ff;font-size:.65rem;font-weight:600">{row['user_name']}</div>
              <div style="color:#b0c4e0;font-size:.72rem;margin-top:2px">{row['comment']}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown('<div class="div"></div>', unsafe_allow_html=True)

    with st.form("comment_form", clear_on_submit=True):
        user    = st.text_input("Your name", "Anonymous")
        comment = st.text_area("Comment", height=70)
        is_emg  = st.checkbox("🚨 Mark as Emergency")
        if st.form_submit_button("Post Comment"):
            supabase.table("comments").insert({
                "project_id": project_id,
                "user_name": user,
                "comment": comment,
                "is_emergency": int(is_emg),
            }).execute()
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)


st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

# ============================  PDF EXPORT  ============================
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown('<div class="section-header">📄 Export Report</div>', unsafe_allow_html=True)

if st.button("📄 Generate PDF Report"):
    buffer = io.BytesIO()
    doc    = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story  = [
        Paragraph(f"{selected_project} – 5D BIM Report", styles["Title"]),
        Spacer(1, 12),
        Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", styles["Normal"]),
        Spacer(1, 8),
        Paragraph(f"SPI: {overall_spi:.3f}  |  CPI: {overall_cpi:.3f}  |  Progress: {overall_progress*100:.1f}%", styles["Normal"]),
        Spacer(1, 6),
        Paragraph(f"Planned Value: {total_pv:,.0f} KES", styles["Normal"]),
        Paragraph(f"Earned Value:  {total_ev:,.0f} KES", styles["Normal"]),
        Paragraph(f"Actual Cost:   {total_ac:,.0f} KES", styles["Normal"]),
        Spacer(1, 6),
        Paragraph(f"Delayed Tasks: {int(delayed_count)}  |  Over Budget: {int(overbudget_count)}  |  On Track: {on_track}", styles["Normal"]),
    ]
    doc.build(story)
    st.download_button(
        "⬇️ Download PDF Report",
        buffer.getvalue(),
        file_name=f"bim_report_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
        mime="application/pdf",
    )

st.markdown("</div>", unsafe_allow_html=True)


st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

# ============================  CONTROLS & FILTERS (bottom) ============================
st.markdown('<div class="section-header" style="opacity:.4;font-size:.75rem;padding:0 .2rem">⚙️ Advanced Controls</div>', unsafe_allow_html=True)

with st.expander("🔍 Filter Data", expanded=False):
    new_cats = st.multiselect("Category", options=_all_cats, default=st.session_state["f_cats"], key="f_cats_widget")
    new_status = st.multiselect("Status", _status_all, default=st.session_state["f_status"], key="f_status_widget")

    def _safe_slider(label, lo, hi, default, key):
        if lo == hi: lo -= 0.1; hi += 0.1
        return st.slider(label, lo, hi, default, key=key)

    new_spi = _safe_slider("SPI Range", _spi_min, _spi_max, st.session_state["f_spi"], "f_spi_widget")
    new_cpi = _safe_slider("CPI Range", _cpi_min, _cpi_max, st.session_state["f_cpi"], "f_cpi_widget")

    if st.button("Apply Filters"):
        st.session_state["f_cats"]   = new_cats
        st.session_state["f_status"] = new_status
        st.session_state["f_spi"]    = new_spi
        st.session_state["f_cpi"]    = new_cpi
        st.rerun()

with st.expander("📐 Quantity Mapping", expanded=False):
    map_response = supabase.table("quantity_mapping").select("category", "quantity_type").execute()
    map_df = pd.DataFrame(map_response.data)
    if map_df.empty:
        # *** FIXED: default for Walls changed from Length to Area ***
        default_mapping = [
            {"category": c, "quantity_type": t} for c, t in [
                ("Walls","Area"),("Columns","Volume"),("Structural Framing","Length"),
                ("Roofs","Area"),("Floors","Area"),("Doors","Count"),("Windows","Count"),
            ]
        ]
        supabase.table("quantity_mapping").insert(default_mapping).execute()
        map_df = pd.DataFrame(default_mapping)
    edited_map = st.data_editor(map_df, use_container_width=True, key="qty_map_editor")
    if st.button("Save Quantity Mapping"):
        for _, row in edited_map.iterrows():
            supabase.table("quantity_mapping").upsert(
                {"category": row["category"], "quantity_type": row["quantity_type"]}
            ).execute()
        st.success("Mapping saved!")

with st.expander("💰 Cost Recalculation", expanded=False):
    if st.button("🔄 Recalculate Costs"):
        c = recalc_costs()
        st.success(f"Recalculated {c} elements.")

with st.expander("📸 Photo Progress Sync", expanded=False):
    if st.button("📸 Update Progress from Photos"):
        updated = update_progress_from_photos()
        if updated: st.success(f"Updated {updated} tasks."); st.rerun()
        else: st.info("No photos with Task ID found.")

with st.expander("✏️ Edit Elements (Unit Cost / Task ID)", expanded=False):
    edit_df      = elements_df[["task_id","unit_cost"]].copy()
    edited_elems = st.data_editor(edit_df, use_container_width=True, key="elem_editor")
    if st.button("Save Element Changes"):
        for _, row in edited_elems.iterrows():
            supabase.table("elements").update({"unit_cost": row["unit_cost"]}).eq("task_id", row["task_id"]).eq("project_id", project_id).execute()
        st.success("Saved!"); st.rerun()

# ============================  FOOTER  ============================
st.markdown(f"""
<div style="text-align:center;padding:2rem 0 1rem;color:#1e2d42;font-size:.65rem;letter-spacing:2px;text-transform:uppercase">
  5D BIM Dashboard · {selected_project} · {today_str}
</div>
""", unsafe_allow_html=True)