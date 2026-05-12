# ============================================================
#  5D BIM Construction Dashboard  –  Dark Neon Fitness Theme
#  (All critical fixes, EVM metrics, Gantt, security)
# ============================================================
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff
import numpy as np
from supabase import create_client
import os
from datetime import datetime, timedelta
import io
import html
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

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

# ============================  MASTER CSS ============================
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


# ============================  PLOTLY THEME ============================
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
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#6a8ab0", size=10)),
    )
    fig.update_xaxes(gridcolor=GRID_CLR, showgrid=False, linecolor=GRID_CLR, tickfont=dict(color=TEXT_CLR, size=10))
    fig.update_yaxes(gridcolor=GRID_CLR, showgrid=True, linecolor="rgba(0,0,0,0)", tickfont=dict(color=TEXT_CLR, size=10))
    return fig


# ============================  SUPABASE (with error handling) ============================
@st.cache_resource
def init_supabase():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = init_supabase()

@st.cache_data(ttl=60)
def load_projects():
    try:
        return pd.DataFrame(supabase.table("projects").select("*").execute().data)
    except Exception as e:
        st.error(f"❌ Could not load projects: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=60)
def load_elements(pid):
    try:
        return pd.DataFrame(supabase.table("elements").select("*").eq("project_id", pid).eq("is_primary", True).execute().data)
    except Exception as e:
        st.error(f"❌ Could not load elements: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=60)
def load_schedule(pid):
    try:
        return pd.DataFrame(supabase.table("schedule_tasks").select("*").eq("project_id", pid).execute().data)
    except Exception as e:
        st.error(f"❌ Could not load schedule: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=60)
def load_comments(pid):
    try:
        return pd.DataFrame(supabase.table("comments").select("*").eq("project_id", pid).order("created_at", desc=True).execute().data)
    except Exception as e:
        st.error(f"❌ Could not load comments: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=60)
def load_photos(pid):
    try:
        return pd.DataFrame(supabase.table("photos").select("*").eq("project_id", pid).order("uploaded_at", desc=True).execute().data)
    except Exception as e:
        st.error(f"❌ Could not load photos: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=60)
def load_spi_history(pid):
    try:
        return pd.DataFrame(supabase.table("spi_history").select("*").eq("project_id", pid).order("recorded_at", desc=True).execute().data)
    except Exception as e:
        st.error(f"❌ Could not load SPI history: {e}")
        return pd.DataFrame()


# ============================  LOAD DATA ============================
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

# ---- Merge & compute (safe division) ----
merged = pd.merge(elements_df, schedule_df, on="task_id", how="inner")
# Replace zero denominators with NaN to avoid division by zero
merged["SPI"] = merged["earned_value"] / merged["planned_value"].replace(0, np.nan)
merged["CPI"] = merged["earned_value"] / merged["actual_cost"].replace(0, np.nan)
# Clip extreme values to avoid broken charts
merged["SPI"] = merged["SPI"].clip(upper=3.0)
merged["CPI"] = merged["CPI"].clip(upper=3.0)
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

# ============================  FILTER STATE (session_state) ============================
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

# ---- Helper functions (optimised) ----
def recalc_costs():
    # One call to get all quantity mappings
    mappings = supabase.table("quantity_mapping").select("category", "quantity_type").execute()
    mapping_dict = {row["category"]: row["quantity_type"] for row in mappings.data}
    updates = []
    for _, elem in elements_df.iterrows():
        qty_type = mapping_dict.get(elem.get("category", ""))
        if not qty_type:
            continue
        quantity = {
            "Volume": elem.get("volume", 0),
            "Area":   elem.get("area", 0),
            "Length": elem.get("length", 0),
            "Count":  elem.get("count", 1),
        }.get(qty_type, 1) or 1
        unit_cost = elem.get("unit_cost", 0) or 0
        updates.append({"id": elem["id"], "total_cost": quantity * unit_cost})
    if updates:
        supabase.table("elements").upsert(updates).execute()
    return len(updates)

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


# ============================  COMPUTE KPIs & EVM Metrics ============================
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
# CORRECT on_track using boolean filter (no double subtraction)
on_track = int(((~filtered["Delayed"]) & (~filtered["OverBudget"])).sum())

# Additional EVM metrics
EAC  = total_pv / overall_cpi if overall_cpi and overall_cpi != 0 else total_pv
ETC  = EAC - total_ac
TCPI = (total_pv - total_ev) / (total_pv - total_ac) if (total_pv - total_ac) != 0 else 1.0

variance_cost  = total_ev - total_ac
variance_sched = total_ev - total_pv

today_str  = datetime.now().strftime("%b %d, %Y")
clock_str  = datetime.now().strftime("%H:%M")

# ---- Real weekly progress (based on schedule dates) ----
if "planned_start" in schedule_df.columns and "planned_finish" in schedule_df.columns:
    schedule_df["planned_start"] = pd.to_datetime(schedule_df["planned_start"])
    schedule_df["planned_finish"] = pd.to_datetime(schedule_df["planned_finish"])
    last_7_days = [(datetime.now() - timedelta(days=i)).date() for i in range(6, -1, -1)]
    daily_progress = []
    for day in last_7_days:
        tasks_should_have_started = schedule_df[schedule_df["planned_start"].dt.date <= day]
        avg_complete = tasks_should_have_started["percent_complete"].mean() / 100 if len(tasks_should_have_started) else 0
        daily_progress.append(avg_complete)
    bar_pcts = daily_progress
    DAYS = ["S","M","T","W","T","F","S"]
else:
    # Fallback: SPI by category (honest label)
    cats = filtered["category"].unique()[:7]
    weekly_spis = [max(0.2, min(1.0, filtered[filtered["category"]==c]["SPI"].mean())) if c in filtered["category"].values else 0.3 for c in cats]
    while len(weekly_spis) < 7: weekly_spis.append(0)
    max_spi    = max(weekly_spis) if max(weekly_spis) > 0 else 1
    bar_pcts   = [v / max_spi for v in weekly_spis]
    DAYS       = [c[:3].upper() for c in cats] if len(cats) == 7 else ["WAL","COL","ROO","FLO","DOO","WIN","OTH"]

def badge(val, lo=0.95, hi=1.0):
    if val >= hi: return '<span class="badge bg">On Track</span>'
    if val >= lo: return '<span class="badge ba">Warning</span>'
    return '<span class="badge br">Behind</span>'

def badge_cpi(val):
    if val >= 1.0: return '<span class="badge bg">Under Budget</span>'
    if val >= 0.9: return '<span class="badge ba">Warning</span>'
    return '<span class="badge br">Over Budget</span>'

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


# ============================  DASHBOARD HEADER + CAPTION ============================
st.markdown(f"""
<div class="dash-header">
  <div>
    <div class="dash-title">🏗️ {selected_project}</div>
    <div class="dash-sub">5D BIM · Construction Performance Dashboard</div>
  </div>
  <div class="dash-time">{clock_str}<br>{today_str}</div>
</div>
""", unsafe_allow_html=True)
st.caption("📌 SPI < 1 = behind schedule | CPI < 1 = over budget | EAC = Estimate at Completion")


# ============================  ROW 1 — OVERVIEW CARDS ============================
c1, c2, c3 = st.columns([1, 1, 1], gap="small")

# Card 1: "This Week" (weekly progress mini‑bar)
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

# Card 2: "Today" — three inline KPI rows
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

# Card 3: SPI/CPI gauges + EAC/ETC/TCPI
with c3:
    spi_pct = min(overall_spi, 1.5) / 1.5
    cpi_pct = min(overall_cpi, 1.5) / 1.5
    spi_col = "#00ff88" if overall_spi >= 0.95 else ("#ffb700" if overall_spi >= 0.8 else "#ff6b6b")
    cpi_col = "#00ff88" if overall_cpi >= 1.0 else ("#ffb700" if overall_cpi >= 0.9 else "#ff6b6b")
    st.markdown(f"""
    <div class="card-dark" style="box-shadow:0 0 22px rgba(168,85,247,0.1)">
      <div class="section-header">Performance & Forecast</div>
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
      <div class="div" style="background:rgba(255,255,255,.1)"></div>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:.6rem">
        <div><span class="label">EAC</span><div class="sm-val" style="font-size:1rem">{EAC/1e6:.2f}M</div></div>
        <div><span class="label">ETC</span><div class="sm-val" style="font-size:1rem">{ETC/1e6:.2f}M</div></div>
        <div><span class="label">TCPI</span><div class="sm-val" style="font-size:1rem">{TCPI:.3f}</div></div>
        <div><span class="label">Progress</span><div class="sm-val" style="font-size:1rem">{overall_progress*100:.0f}%</div></div>
      </div>
      <div style="display:flex;gap:.5rem;flex-wrap:wrap;margin-top:.8rem">
        <span class="badge {'bg' if overall_spi>=0.95 else 'br'}">{int(delayed_count)} delayed</span>
        <span class="badge {'bg' if overall_cpi>=1.0 else 'br'}">{int(overbudget_count)} over budget</span>
      </div>
      <div class="brand">BIM</div>
    </div>
    """, unsafe_allow_html=True)


st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

# ============================  ROW 2 — GRADIENT CARD + DONUT ============================
col_left, col_right = st.columns([3, 2], gap="small")

with col_left:
    vcost_disp   = f"+{variance_cost/1e3:.0f}K" if variance_cost >= 0 else f"{variance_cost/1e3:.0f}K"
    vsched_disp  = f"+{variance_sched/1e3:.0f}K" if variance_sched >= 0 else f"{variance_sched/1e3:.0f}K"
    vcost_col    = "#00ff88" if variance_cost >= 