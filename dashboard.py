# ============================================================
#  5D BIM Construction Dashboard
#  All objectives addressed — full fixes applied
# ============================================================
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from supabase import create_client
import os, io, html
from datetime import datetime, timedelta
from reportlab.lib.pagesizes import A4
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer,
                                 Table, TableStyle, HRFlowable)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors as rl_colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.units import cm

# ── CONFIG ──────────────────────────────────────────────────
SUPABASE_URL = st.secrets.get("supabase_url", os.environ.get("SUPABASE_URL",""))
SUPABASE_KEY = st.secrets.get("supabase_key", os.environ.get("SUPABASE_KEY",""))

st.set_page_config(page_title="5D BIM Dashboard", page_icon="🏗️",
                   layout="wide", initial_sidebar_state="collapsed")

# ════════════════════════════════════════════════════════════
#  MASTER CSS  — matches screenshot exactly
# ════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

*{box-sizing:border-box;margin:0;padding:0;}
html,body,.stApp{background:#090b0f!important;font-family:'DM Sans',sans-serif;color:#dce8ff;}

header[data-testid="stHeader"],#MainMenu,footer,.stDeployButton,
div[data-testid="stToolbar"],div[data-testid="stDecoration"],
div[data-testid="stMetric"]{display:none!important;}

.block-container{padding:1rem 1.5rem 2rem!important;max-width:100%!important;}

/* ── CARDS ── */
.card{background:#111622;border:1px solid rgba(255,255,255,.07);border-radius:22px;
      padding:1.2rem 1.3rem;position:relative;overflow:hidden;height:100%;}
.card-gradient{background:linear-gradient(145deg,#2a1765 0%,#6b1878 48%,#c42760 100%);
               border-radius:22px;padding:1.2rem 1.3rem;position:relative;overflow:hidden;height:100%;}
.card-gradient::after{content:'';position:absolute;top:-50px;right:-50px;width:200px;height:200px;
  background:radial-gradient(circle,rgba(255,80,200,.28) 0%,transparent 70%);pointer-events:none;}
.card-dark{background:#0d101a;border:1px solid rgba(255,255,255,.05);border-radius:22px;
           padding:1.2rem 1.3rem;position:relative;overflow:hidden;height:100%;}

/* ── TYPOGRAPHY ── */
.label{color:#5a6a8a;font-size:.82rem;text-transform:uppercase;letter-spacing:1.8px;
       font-weight:500;margin-bottom:2px;}
.big-val{color:#eef4ff;font-size:2.6rem;font-weight:700;font-family:'JetBrains Mono',monospace;line-height:1.05;}
.med-val{color:#eef4ff;font-size:1.5rem;font-weight:600;font-family:'JetBrains Mono',monospace;line-height:1.1;}
.sm-val{color:#eef4ff;font-size:1.05rem;font-weight:600;font-family:'JetBrains Mono',monospace;}
.sub{color:rgba(255,255,255,.38);font-size:.7rem;font-weight:400;margin-left:3px;}
.section-header{color:#eef4ff;font-size:.82rem;font-weight:700;text-transform:uppercase;
                letter-spacing:2px;margin-bottom:.9rem;opacity:.65;}
.brand{position:absolute;bottom:.85rem;right:1rem;font-size:.54rem;color:rgba(255,255,255,.15);
       text-transform:uppercase;letter-spacing:2.5px;font-weight:600;}

/* ── BADGES ── */
.badge{display:inline-flex;align-items:center;padding:3px 11px;border-radius:999px;
       font-size:.72rem;font-weight:700;letter-spacing:.5px;text-transform:uppercase;}
.bg{background:rgba(0,255,136,.13);color:#00ff88;border:1px solid rgba(0,255,136,.32);}
.br{background:rgba(255,70,70,.13);color:#ff6b6b;border:1px solid rgba(255,70,70,.32);}
.ba{background:rgba(255,183,0,.13);color:#ffb700;border:1px solid rgba(255,183,0,.32);}
.bb{background:rgba(0,160,255,.13);color:#00aaff;border:1px solid rgba(0,160,255,.32);}
.bp{background:rgba(168,85,247,.13);color:#c084fc;border:1px solid rgba(168,85,247,.32);}

/* ── MINI BARS ── */
.mini-bars{display:flex;align-items:flex-end;gap:6px;height:54px;margin-top:.7rem;}
.mb{flex:1;border-radius:5px 5px 0 0;min-height:5px;}
.mb-green{background:#00ff88;} .mb-pink{background:#ff3d9a;} .mb-dim{background:#1a2535;}
.day-row{display:flex;gap:6px;margin-top:4px;}
.day-row span{flex:1;text-align:center;font-size:.55rem;color:#2e3d50;text-transform:uppercase;}

/* ── KPI ROWS ── */
.kpi-row{display:flex;align-items:center;gap:.55rem;padding:.48rem 0;
         border-bottom:1px solid rgba(255,255,255,.04);}
.kpi-row:last-child{border-bottom:none;}
.kpi-icon{font-size:1.1rem;width:24px;text-align:center;}
.kpi-text{flex:1;}
.kpi-label{font-size:.76rem;color:#5a6a8a;text-transform:uppercase;letter-spacing:1px;}
.kpi-val{font-size:1.05rem;font-weight:600;color:#eef4ff;font-family:'JetBrains Mono',monospace;}
.kpi-badge{margin-left:auto;}

/* ── PROGRESS BARS ── */
.pbar-wrap{background:rgba(255,255,255,.07);border-radius:999px;height:5px;
           margin-top:5px;overflow:hidden;}
.pbar-fill{height:100%;border-radius:999px;background:linear-gradient(90deg,#00ff88,#00e0cc);transition:width .5s;}
.pbar-pink{height:100%;border-radius:999px;background:linear-gradient(90deg,#ff3d9a,#ff8c42);transition:width .5s;}
.pbar-amber{height:100%;border-radius:999px;background:linear-gradient(90deg,#ffb700,#ff8c42);transition:width .5s;}

/* ── STAT LABELS (gradient card) ── */
.stat-label{color:rgba(255,255,255,.42);font-size:.7rem;text-transform:uppercase;letter-spacing:1.4px;}
.stat-val{color:#fff;font-size:1.05rem;font-weight:600;font-family:'JetBrains Mono',monospace;}
.stat-val-lg{color:#fff;font-size:1.5rem;font-weight:700;font-family:'JetBrains Mono',monospace;}
.stat-sub{color:rgba(255,255,255,.3);font-size:.58rem;}

/* ── DIVIDER ── */
.div{height:1px;background:linear-gradient(90deg,transparent,rgba(255,255,255,.09),transparent);margin:.9rem 0;}

/* ── HEADER ── */
.dash-header{display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:1.1rem;}
.dash-title{font-size:1.65rem;font-weight:700;color:#eef4ff;letter-spacing:-.3px;}
.dash-sub{font-size:.68rem;color:#2e3d50;margin-top:4px;letter-spacing:.5px;}
.dash-time{font-size:.7rem;color:#2e3d50;font-family:'JetBrains Mono',monospace;text-align:right;line-height:1.7;}

/* ── ALERT BOXES ── */
.alert-red{background:rgba(255,60,60,.07);border:1px solid rgba(255,107,107,.22);
           border-radius:14px;padding:.7rem 1rem;margin-bottom:.5rem;}
.alert-green{background:rgba(0,255,136,.07);border:1px solid rgba(0,255,136,.22);
             border-radius:14px;padding:.7rem 1rem;}
.alert-amber{background:rgba(255,183,0,.07);border:1px solid rgba(255,183,0,.22);
             border-radius:14px;padding:.7rem 1rem;margin-bottom:.5rem;}
.comment-emg{background:rgba(255,60,60,.07);border-left:3px solid #ff6b6b;
             border-radius:0 10px 10px 0;padding:.5rem .75rem;margin-bottom:.5rem;}
.comment-norm{background:rgba(255,255,255,.025);border-left:3px solid #1e3050;
              border-radius:0 10px 10px 0;padding:.5rem .75rem;margin-bottom:.5rem;}

/* ── INTEGRATION HEALTH ── */
.health-row{display:flex;align-items:center;justify-content:space-between;
            padding:.5rem 0;border-bottom:1px solid rgba(255,255,255,.04);}
.health-row:last-child{border-bottom:none;}

/* ── STREAMLIT OVERRIDES ── */
.stSelectbox label,.stMultiSelect label,.stSlider label,.stNumberInput label{
  color:#5a6a8a!important;font-size:.72rem!important;text-transform:uppercase;letter-spacing:1px;}
div[data-baseweb="select"]>div{background:#0d101a!important;border-color:rgba(255,255,255,.1)!important;
  border-radius:12px!important;color:#eef4ff!important;}
.stButton>button{background:linear-gradient(135deg,#131d33,#0d1422);
  border:1px solid rgba(0,160,255,.25);border-radius:40px;color:#6ab4ff;
  font-family:'DM Sans',sans-serif;font-size:.78rem;font-weight:500;
  width:100%;padding:.45rem 1rem;transition:all .2s;}
.stButton>button:hover{border-color:#00aaff;box-shadow:0 0 16px rgba(0,160,255,.3);color:#aad6ff;}
h1,h2,h3{color:#c5deff!important;font-weight:600;}
div[data-testid="stExpander"]{background:#0d101a;border:1px solid rgba(255,255,255,.06);
  border-radius:16px;padding:.2rem .4rem;}
div[data-testid="stExpander"] summary{color:#6a8ab0!important;}
div[data-testid="stPlotlyChart"]{border-radius:18px;overflow:hidden;}
div[data-testid="stAlert"]{border-radius:14px!important;background:#0d101a!important;}
.stDataFrame{border-radius:16px!important;overflow:hidden;}
::-webkit-scrollbar{width:4px;height:4px;}
::-webkit-scrollbar-track{background:#090b0f;}
::-webkit-scrollbar-thumb{background:#1e2d4a;border-radius:4px;}
</style>
""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════
#  COLOUR CONSTANTS + CHART HELPERS
# ════════════════════════════════════════════════════════════
GREEN  = "#00ff88";  PINK   = "#ff3d9a";  BLUE  = "#00aaff"
AMBER  = "#ffb700";  PURPLE = "#a855f7";  TEAL  = "#00e0cc"
ORANGE = "#ff8c42";  RED    = "#ff6b6b"
RING   = [BLUE,ORANGE,PINK,GREEN,PURPLE,AMBER,TEAL,"#e879f9","#34d399","#f472b6"]

def dark_fig(fig):
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="DM Sans",color="#5a6a8a",size=11),
        margin=dict(l=10,r=10,t=35,b=10),
        legend=dict(bgcolor="rgba(0,0,0,0)",font=dict(color="#6a8ab0",size=10)))
    fig.update_xaxes(gridcolor="rgba(255,255,255,.04)",showgrid=False,
        linecolor="rgba(255,255,255,.04)",tickfont=dict(color="#5a6a8a",size=10))
    fig.update_yaxes(gridcolor="rgba(255,255,255,.04)",showgrid=True,
        linecolor="rgba(0,0,0,0)",tickfont=dict(color="#5a6a8a",size=10))
    return fig

def badge(v,lo=0.95):
    if v>=1.0: return '<span class="badge bg">On Track</span>'
    if v>=lo:  return '<span class="badge ba">Warning</span>'
    return '<span class="badge br">Behind</span>'

def badge_cpi(v):
    if v>=1.0: return '<span class="badge bg">Under Budget</span>'
    if v>=0.9: return '<span class="badge ba">Warning</span>'
    return '<span class="badge br">Over Budget</span>'

def pbar(pct,cls="pbar-fill"):
    return f'<div class="pbar-wrap"><div class="{cls}" style="width:{min(pct*100,100):.1f}%"></div></div>'

def mini_bars_html(heights):
    DAYS=["S","M","T","W","T","F","S"]
    today_idx=(datetime.now().weekday()+1)%7
    bars="".join(
        f'<div class="mb {"mb-green" if i<today_idx else "mb-pink" if i==today_idx else "mb-dim"}" '
        f'style="height:{max(5,int(h*54))}px"></div>' for i,h in enumerate(heights))
    spans="".join(f"<span>{d}</span>" for d in DAYS)
    return f'<div class="mini-bars">{bars}</div><div class="day-row">{spans}</div>'

def fmt(v,d=2):
    v=float(v)
    if abs(v)>=1e6: return f"{v/1e6:.{d}f}M"
    if abs(v)>=1e3: return f"{v/1e3:.{d}f}K"
    return f"{v:.{d}f}"

def signed(v):
    s=fmt(v); return f"+{s}" if v>=0 else s
def scol(v): return GREEN if v>=0 else RED

# ════════════════════════════════════════════════════════════
#  SUPABASE  — all calls wrapped in try/except
# ════════════════════════════════════════════════════════════
@st.cache_resource
def init_sb(): return create_client(SUPABASE_URL,SUPABASE_KEY)
supabase=init_sb()

def _q(fn):
    try: return fn()
    except Exception as e: st.error(f"DB error: {e}"); return []

@st.cache_data(ttl=60)
def load_projects():
    d=_q(lambda:supabase.table("projects").select("*").execute().data)
    return pd.DataFrame(d)

@st.cache_data(ttl=60)
def load_elements(pid):
    d=_q(lambda:supabase.table("elements").select("*")
         .eq("project_id",pid).execute().data)
    return pd.DataFrame(d)

@st.cache_data(ttl=60)
def load_schedule(pid):
    d=_q(lambda:supabase.table("schedule_tasks").select("*")
         .eq("project_id",pid).execute().data)
    return pd.DataFrame(d)

@st.cache_data(ttl=60)
def load_comments(pid):
    d=_q(lambda:supabase.table("comments").select("*")
         .eq("project_id",pid).order("created_at",desc=True).execute().data)
    return pd.DataFrame(d)

@st.cache_data(ttl=60)
def load_photos(pid):
    d=_q(lambda:supabase.table("photos").select("*")
         .eq("project_id",pid).order("uploaded_at",desc=True).execute().data)
    return pd.DataFrame(d)

@st.cache_data(ttl=60)
def load_spi_history(pid):
    d=_q(lambda:supabase.table("spi_history").select("*")
         .eq("project_id",pid).order("recorded_at",desc=False).execute().data)
    return pd.DataFrame(d)

# ════════════════════════════════════════════════════════════
#  LOAD PROJECT
# ════════════════════════════════════════════════════════════
projects_df=load_projects()
if projects_df.empty: st.warning("No projects found."); st.stop()

selected_project=st.sidebar.selectbox("🏢 Project",projects_df["name"].tolist())
project_id=projects_df[projects_df["name"]==selected_project]["id"].iloc[0]

elements_df  =load_elements(project_id)
schedule_df  =load_schedule(project_id)
comments_df  =load_comments(project_id)
photos_df    =load_photos(project_id)
spi_hist_df  =load_spi_history(project_id)

if elements_df.empty or schedule_df.empty:
    st.warning("No data found. Run the sync tool first."); st.stop()

# ════════════════════════════════════════════════════════════
#  MERGE + SAFE COMPUTATION  (FIX: div/0, percent_complete cap)
# ════════════════════════════════════════════════════════════
merged=pd.merge(elements_df,schedule_df,on="task_id",how="inner")

# FIX 1 — safe division, no crash
merged["SPI"]=(merged["earned_value"]/
               merged["planned_value"].replace(0,np.nan)).clip(upper=3.0).fillna(0)
merged["CPI"]=(merged["earned_value"]/
               merged["actual_cost"].replace(0,np.nan)).clip(upper=3.0).fillna(0)

# FIX 2 — cap percent_complete 0–100
if "percent_complete" in merged.columns:
    merged["percent_complete"]=merged["percent_complete"].clip(0,100)

merged["Delayed"]   =merged["SPI"]<1.0
merged["OverBudget"]=merged["CPI"]<1.0

# ════════════════════════════════════════════════════════════
#  SIDEBAR
# ════════════════════════════════════════════════════════════
st.sidebar.markdown("## ⚙️ Controls")
extra_cost=st.sidebar.number_input("Extra Cost (KES)",value=0,step=1000)
proj_res=supabase.table("projects").select("extra_cost").eq("id",project_id).execute()
curr_extra=proj_res.data[0]["extra_cost"] if proj_res.data else 0
if extra_cost!=curr_extra:
    supabase.table("projects").update({"extra_cost":extra_cost}).eq("id",project_id).execute()
    st.sidebar.success("Updated")

st.sidebar.markdown("---")
st.sidebar.markdown("### ⚠️ Alert Thresholds")
spi_warn_thresh=st.sidebar.slider("SPI Warning below",0.70,1.0,0.95,0.01)
cpi_warn_thresh=st.sidebar.slider("CPI Warning below",0.70,1.0,0.90,0.01)

# ════════════════════════════════════════════════════════════
#  FILTER STATE  (session_state; widgets at bottom)
# ════════════════════════════════════════════════════════════
_all_cats=list(merged["category"].unique())
_sta_all=["On Track","Delayed","Over Budget","Delayed & Over"]
_spi_mn=float(merged["SPI"].min()); _spi_mx=float(merged["SPI"].max())
_cpi_mn=float(merged["CPI"].min()); _cpi_mx=float(merged["CPI"].max())
if _spi_mn==_spi_mx: _spi_mn-=0.1; _spi_mx+=0.1
if _cpi_mn==_cpi_mx: _cpi_mn-=0.1; _cpi_mx+=0.1

for k,v in [("f_cats",_all_cats),("f_sta",_sta_all),
            ("f_spi",(_spi_mn,_spi_mx)),("f_cpi",(_cpi_mn,_cpi_mx))]:
    if k not in st.session_state: st.session_state[k]=v

sf=st.session_state["f_sta"]
conds=[]
if "On Track"       in sf: conds.append((~merged["Delayed"])&(~merged["OverBudget"]))
if "Delayed"        in sf: conds.append(merged["Delayed"]&(~merged["OverBudget"]))
if "Over Budget"    in sf: conds.append((~merged["Delayed"])&merged["OverBudget"])
if "Delayed & Over" in sf: conds.append(merged["Delayed"]&merged["OverBudget"])
fs=conds[0] if conds else pd.Series([True]*len(merged))
for c in conds[1:]: fs|=c

slo,shi=st.session_state["f_spi"]; clo,chi=st.session_state["f_cpi"]
filtered=merged[merged["category"].isin(st.session_state["f_cats"])
                &fs&merged["SPI"].between(slo,shi)&merged["CPI"].between(clo,chi)]

# ════════════════════════════════════════════════════════════
#  HELPER FUNCTIONS
# ════════════════════════════════════════════════════════════
def recalc_costs():
    """Batch recalc — 2 DB calls total, not N."""
    mp=supabase.table("quantity_mapping").select("category","quantity_type").execute()
    mdict={r["category"]:r["quantity_type"] for r in mp.data}
    ups=[]
    for _,e in elements_df.iterrows():
        qt=mdict.get(e.get("category",""))
        if not qt: continue
        qty={"Volume":e.get("volume",0),"Area":e.get("area",0),
             "Length":e.get("length",0),"Count":e.get("count",1)}.get(qt,1) or 1
        uc=e.get("unit_cost",0) or 0
        ups.append({"id":e["id"],"total_cost":qty*uc})
    if ups: supabase.table("elements").upsert(ups).execute()
    return len(ups)

def update_progress_from_photos():
    ph=supabase.table("photos").select("task_id","completion_status","uploaded_at")\
               .eq("project_id",project_id).execute()
    if not ph.data: return 0
    latest={}
    for p in ph.data:
        tid=p["task_id"]
        if not tid: continue
        if tid not in latest or p["uploaded_at"]>latest[tid]["uploaded_at"]: latest[tid]=p
    count=0
    for tid,info in latest.items():
        pct={"Not Started":0,"In Progress":50,"Complete":100}.get(
            info.get("completion_status","Not Started"),0)
        supabase.table("schedule_tasks").update({"percent_complete":pct})\
                .eq("project_id",project_id).eq("task_id",tid).execute()
        count+=1
    return count

# ════════════════════════════════════════════════════════════
#  KPI COMPUTATIONS  (all fixes applied)
# ════════════════════════════════════════════════════════════
total_pv      =filtered["planned_value"].sum()
total_ev      =filtered["earned_value"].sum()
total_ac      =filtered["actual_cost"].sum()
total_bim_cost=filtered["total_cost"].sum() if "total_cost" in filtered.columns else 0

overall_spi =total_ev/total_pv  if total_pv  else 1.0
overall_cpi =total_ev/total_ac  if total_ac  else 1.0
# FIX 3 — cap progress at 100%
overall_prog=min((filtered["percent_complete"]*filtered["planned_value"]).sum()/total_pv,1.0) if total_pv else 0

total_length    =filtered["length"].sum() if "length" in filtered.columns else 0
num_elements    =len(filtered)
num_categories  =filtered["category"].nunique()
delayed_count   =int(filtered["Delayed"].sum())
overbudget_count=int(filtered["OverBudget"].sum())
# FIX 4 — correct on_track formula (no double-counting)
on_track=int(((~filtered["Delayed"])&(~filtered["OverBudget"])).sum())

vc=total_ev-total_ac; vs=total_ev-total_pv

# FIX 5 — EAC / ETC / TCPI (missing in old code)
EAC =total_pv/overall_cpi if overall_cpi else total_pv
ETC =EAC-total_ac
TCPI=(total_pv-total_ev)/(total_pv-total_ac) if (total_pv-total_ac)!=0 else 1.0
tcpi_col=GREEN if TCPI<=1.1 else (AMBER if TCPI<=1.25 else RED)

# FIX 6 — real project duration from schedule dates
planned_duration=100
for sc,fc in [("start_date","finish_date"),("planned_start","planned_finish")]:
    if sc in schedule_df.columns and fc in schedule_df.columns:
        try:
            sd=pd.to_datetime(schedule_df[sc],errors="coerce")
            fd=pd.to_datetime(schedule_df[fc],errors="coerce")
            dur=int((fd.max()-sd.min()).days)
            if dur>0: planned_duration=dur; break
        except: pass

today_str=datetime.now().strftime("%b %d, %Y")
clock_str=datetime.now().strftime("%H:%M")

# Mini-bar data (SPI per category)
cats7=list(filtered["category"].unique())[:7]
wv=[float(filtered[filtered["category"]==c]["SPI"].mean()) if len(filtered[filtered["category"]==c]) else 0.3 for c in cats7]
while len(wv)<7: wv.append(0)
wv=wv[:7]; mx=max(wv) if max(wv)>0 else 1
bar_pcts=[v/mx for v in wv]

cat_ev_df   =filtered.groupby("category")["earned_value"].sum().reset_index()
cost_by_cat =filtered.groupby("category")["total_cost"].sum().reset_index()\
                      .sort_values("total_cost",ascending=False)

# ════════════════════════════════════════════════════════════
#  INTEGRATION HEALTH  (NEW — Objective 1)
# ════════════════════════════════════════════════════════════
all_revit_tids   =set(elements_df["task_id"].dropna().unique()) if not elements_df.empty else set()
all_sched_tids   =set(schedule_df["task_id"].dropna().unique()) if not schedule_df.empty else set()
matched_tids     =all_revit_tids & all_sched_tids
revit_only_tids  =all_revit_tids - all_sched_tids
sched_only_tids  =all_sched_tids - all_revit_tids
match_rate       =len(matched_tids)/len(all_revit_tids)*100 if all_revit_tids else 0

# ════════════════════════════════════════════════════════════
#  DASHBOARD HEADER
# ════════════════════════════════════════════════════════════
st.markdown(f"""
<div class="dash-header">
  <div>
    <div class="dash-title">🏗️ {selected_project}</div>
    <div class="dash-sub">5D BIM · Construction Performance Dashboard</div>
  </div>
  <div class="dash-time">{clock_str}<br>{today_str}</div>
</div>""",unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════
#  ROW 1 — THREE OVERVIEW CARDS
# ════════════════════════════════════════════════════════════
c1,c2,c3=st.columns([1,1,1],gap="small")

with c1:
    prog_pct=overall_prog*100
    st.markdown(f"""
    <div class="card" style="box-shadow:0 0 28px rgba(0,255,136,.07)">
      <div class="section-header">This Week</div>
      <div style="display:flex;justify-content:space-between;align-items:flex-start">
        <div>
          <div class="label">Progress</div>
          <div class="big-val">{prog_pct:.1f}<span class="sub">%</span></div>
        </div>
        <div style="text-align:right">
          <div class="label">Tasks</div>
          <div class="med-val">{on_track}<span class="sub">/{num_elements}</span></div>
          <div style="margin-top:5px">{badge(overall_spi,spi_warn_thresh)}</div>
        </div>
      </div>
      {mini_bars_html(bar_pcts)}
      <div class="brand">BIM</div>
    </div>""",unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="card" style="box-shadow:0 0 28px rgba(0,160,255,.06)">
      <div class="section-header">Today</div>
      <div class="kpi-row">
        <div class="kpi-icon">📐</div>
        <div class="kpi-text"><div class="kpi-label">Earned Value</div>
          <div class="kpi-val">{fmt(total_ev)} KES</div></div>
        <div class="kpi-badge">{badge(overall_spi,spi_warn_thresh)}</div>
      </div>
      <div class="kpi-row">
        <div class="kpi-icon">📋</div>
        <div class="kpi-text"><div class="kpi-label">Planned Value</div>
          <div class="kpi-val">{fmt(total_pv)} KES</div></div>
        <div class="kpi-badge"><span class="badge bb">Planned</span></div>
      </div>
      <div class="kpi-row">
        <div class="kpi-icon">🔥</div>
        <div class="kpi-text"><div class="kpi-label">Actual Cost</div>
          <div class="kpi-val">{fmt(total_ac)} KES</div></div>
        <div class="kpi-badge">{badge_cpi(overall_cpi)}</div>
      </div>
      <div class="brand">BIM</div>
    </div>""",unsafe_allow_html=True)

with c3:
    spi_pct=min(overall_spi/1.5,1.0); cpi_pct=min(overall_cpi/1.5,1.0)
    spi_col=GREEN if overall_spi>=spi_warn_thresh else (AMBER if overall_spi>=0.8 else RED)
    cpi_col=GREEN if overall_cpi>=1.0 else (AMBER if overall_cpi>=cpi_warn_thresh else RED)
    spi_cls="pbar-fill" if overall_spi>=spi_warn_thresh else ("pbar-amber" if overall_spi>=0.8 else "pbar-pink")
    cpi_cls="pbar-fill" if overall_cpi>=1.0 else ("pbar-amber" if overall_cpi>=cpi_warn_thresh else "pbar-pink")
    st.markdown(f"""
    <div class="card-dark" style="box-shadow:0 0 28px rgba(168,85,247,.08)">
      <div class="section-header">Performance</div>
      <div style="margin-bottom:1rem">
        <div style="display:flex;justify-content:space-between;align-items:baseline">
          <div class="label">Schedule Performance</div>
          <div class="sm-val" style="color:{spi_col}">{overall_spi:.3f}</div>
        </div>
        <div class="pbar-wrap"><div class="{spi_cls}" style="width:{spi_pct*100:.1f}%"></div></div>
      </div>
      <div style="margin-bottom:1rem">
        <div style="display:flex;justify-content:space-between;align-items:baseline">
          <div class="label">Cost Performance</div>
          <div class="sm-val" style="color:{cpi_col}">{overall_cpi:.3f}</div>
        </div>
        <div class="pbar-wrap"><div class="{cpi_cls}" style="width:{cpi_pct*100:.1f}%"></div></div>
      </div>
      <div style="display:flex;gap:.5rem;flex-wrap:wrap">
        <span class="badge {'bg' if delayed_count==0 else 'br'}">{delayed_count} Delayed</span>
        <span class="badge {'bg' if overbudget_count==0 else 'br'}">{overbudget_count} Over Budget</span>
      </div>
      <div class="brand">BIM</div>
    </div>""",unsafe_allow_html=True)

st.markdown("<div style='height:14px'></div>",unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════
#  ROW 2 — GRADIENT CARD + DONUT
# ════════════════════════════════════════════════════════════
col_grad,col_donut=st.columns([3,2],gap="small")

with col_grad:
    ld_disp=f"{total_length:,.1f}" if total_length else "—"
    st.markdown(f"""
    <div class="card-gradient">
      <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:1rem;margin-bottom:.85rem">
        <div><div class="stat-label">Planned Value</div>
             <div class="stat-val-lg">{fmt(total_pv)}</div><div class="stat-sub">KES</div></div>
        <div><div class="stat-label">Earned Value</div>
             <div class="stat-val-lg">{fmt(total_ev)}</div><div class="stat-sub">KES</div></div>
        <div><div class="stat-label">Actual Cost</div>
             <div class="stat-val-lg">{fmt(total_ac)}</div><div class="stat-sub">KES</div></div>
      </div>
      <div style="height:1px;background:rgba(255,255,255,.12);margin:.55rem 0"></div>
      <div style="display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:.8rem;margin-bottom:.85rem">
        <div><div class="stat-label">SPI</div><div class="stat-val">{overall_spi:.3f}</div></div>
        <div><div class="stat-label">CPI</div><div class="stat-val">{overall_cpi:.3f}</div></div>
        <div><div class="stat-label">Cost Var</div>
             <div class="stat-val" style="color:{'#00ff88' if vc>=0 else '#ff6b6b'}">{signed(vc)}</div></div>
        <div><div class="stat-label">Sched Var</div>
             <div class="stat-val" style="color:{'#00ff88' if vs>=0 else '#ff6b6b'}">{signed(vs)}</div></div>
      </div>
      <div style="height:1px;background:rgba(255,255,255,.12);margin:.55rem 0"></div>
      <div style="display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:.8rem;margin-bottom:.85rem">
        <div><div class="stat-label">EAC</div><div class="stat-val">{fmt(EAC)}</div></div>
        <div><div class="stat-label">ETC</div><div class="stat-val">{fmt(ETC)}</div></div>
        <div><div class="stat-label">TCPI</div>
             <div class="stat-val" style="color:{tcpi_col}">{TCPI:.3f}</div></div>
        <div><div class="stat-label">Progress</div>
             <div class="stat-val">{overall_prog*100:.1f}%</div></div>
      </div>
      <div style="height:1px;background:rgba(255,255,255,.12);margin:.55rem 0"></div>
      <div style="display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:.8rem">
        <div><div class="stat-label">Elements</div><div class="stat-val">{num_elements}</div></div>
        <div><div class="stat-label">Categories</div><div class="stat-val">{num_categories}</div></div>
        <div><div class="stat-label">Length</div><div class="stat-val">{ld_disp} m</div></div>
        <div><div class="stat-label">Extra Cost</div><div class="stat-val">{extra_cost:,.0f}</div></div>
      </div>
      <div class="brand" style="color:rgba(255,255,255,.18)">BIM</div>
    </div>""",unsafe_allow_html=True)

with col_donut:
    fig_d=go.Figure(go.Pie(
        labels=cat_ev_df["category"],values=cat_ev_df["earned_value"],hole=0.62,
        marker=dict(colors=RING[:len(cat_ev_df)],line=dict(color="#090b0f",width=3)),
        textinfo="none",hovertemplate="<b>%{label}</b><br>EV: %{value:,.0f} KES<extra></extra>"))
    fig_d.add_annotation(text=f"<b>{overall_prog*100:.0f}%</b><br><span style='font-size:10px'>Done</span>",
        x=0.5,y=0.5,showarrow=False,font=dict(size=20,color="#eef4ff"),align="center")
    fig_d.update_layout(title=dict(text="EV by Category",font=dict(color="#8aa2c0",size=13)),
        height=300,showlegend=True,
        legend=dict(bgcolor="rgba(0,0,0,0)",font=dict(color="#5a6a8a",size=10),
                    orientation="v",x=1.02,y=0.5),
        margin=dict(l=0,r=90,t=40,b=10),
        paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)")
    st.markdown('<div class="card-dark" style="box-shadow:0 0 22px rgba(168,85,247,.08)">',unsafe_allow_html=True)
    st.plotly_chart(fig_d,use_container_width=True,config={"displayModeBar":False})
    st.markdown("</div>",unsafe_allow_html=True)

st.markdown("<div style='height:14px'></div>",unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════
#  ROW 3 — BAR CHARTS
# ════════════════════════════════════════════════════════════
bc1,bc2=st.columns([1,1],gap="small")

with bc1:
    cs=filtered.groupby("category").agg({"planned_value":"sum","actual_cost":"sum"}).reset_index()
    fb=go.Figure()
    fb.add_trace(go.Bar(name="Planned",x=cs["category"],y=cs["planned_value"],marker_color=BLUE,opacity=0.85))
    fb.add_trace(go.Bar(name="Actual Cost",x=cs["category"],y=cs["actual_cost"],marker_color=GREEN,opacity=0.85))
    fb.update_layout(barmode="group",title=dict(text="Planned vs Actual Cost",font=dict(color="#8aa2c0",size=12)),height=270)
    st.markdown('<div class="card">',unsafe_allow_html=True)
    st.plotly_chart(dark_fig(fb),use_container_width=True,config={"displayModeBar":False})
    st.markdown("</div>",unsafe_allow_html=True)

with bc2:
    cp=filtered.groupby("category").agg({"SPI":"mean","CPI":"mean"}).reset_index()
    fp=go.Figure()
    fp.add_trace(go.Bar(name="SPI",x=cp["category"],y=cp["SPI"],marker_color=PINK,opacity=0.9))
    fp.add_trace(go.Bar(name="CPI",x=cp["category"],y=cp["CPI"],marker_color=AMBER,opacity=0.9))
    fp.add_hline(y=1.0,line_dash="dot",line_color=GREEN,line_width=1,
                 annotation_text="Target 1.0",annotation_font_color=GREEN,annotation_font_size=9)
    fp.add_hline(y=spi_warn_thresh,line_dash="dot",line_color=AMBER,line_width=1,
                 annotation_text=f"Warn {spi_warn_thresh}",annotation_font_color=AMBER,annotation_font_size=9)
    fp.update_layout(barmode="group",title=dict(text="SPI & CPI by Category",font=dict(color="#8aa2c0",size=12)),height=270)
    st.markdown('<div class="card">',unsafe_allow_html=True)
    st.plotly_chart(dark_fig(fp),use_container_width=True,config={"displayModeBar":False})
    st.markdown("</div>",unsafe_allow_html=True)

st.markdown("<div style='height:14px'></div>",unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════
#  NEW — S-CURVE  (Objective 3: synthesise real-time metrics)
# ════════════════════════════════════════════════════════════
st.markdown('<div class="card">',unsafe_allow_html=True)
st.markdown('<div class="section-header">📈 S-Curve — Cumulative EVM Over Time</div>',unsafe_allow_html=True)

date_col=next((c for c in ["start_date","planned_start"] if c in schedule_df.columns),None)
if not spi_hist_df.empty and {"recorded_at","spi"}.issubset(spi_hist_df.columns):
    sh=spi_hist_df.copy()
    sh["recorded_at"]=pd.to_datetime(sh["recorded_at"],errors="coerce")
    sh["spi"]=pd.to_numeric(sh["spi"],errors="coerce")
    if "cpi" in sh.columns:
        sh["cpi"]=pd.to_numeric(sh["cpi"],errors="coerce")
    sh=sh.replace([np.inf,-np.inf],np.nan).dropna(subset=["recorded_at","spi"]).sort_values("recorded_at")
    agg_cols={"spi":"mean"}
    if "cpi" in sh.columns and sh["cpi"].notna().any():
        agg_cols["cpi"]="mean"
    daily=sh.groupby("recorded_at").agg(agg_cols).reset_index()
    daily["cum_spi"]=daily["spi"].expanding().mean()
    fig_sc=go.Figure()
    fig_sc.add_trace(go.Scatter(x=daily["recorded_at"],y=daily["cum_spi"],name="Avg SPI",
        line=dict(color=GREEN,width=2.5),mode="lines+markers",
        marker=dict(size=5,color=GREEN)))
    if "cpi" in daily.columns:
        daily["cum_cpi"]=daily["cpi"].expanding().mean()
        fig_sc.add_trace(go.Scatter(x=daily["recorded_at"],y=daily["cum_cpi"],name="Avg CPI",
            line=dict(color=AMBER,width=2.5),mode="lines+markers",
            marker=dict(size=5,color=AMBER)))
    fig_sc.add_hline(y=1.0,line_dash="dot",line_color=PINK,line_width=1,
                     annotation_text="Ideal=1.0",annotation_font_color=PINK,annotation_font_size=9)
    trend_title="SPI & CPI Trend (S-Curve)" if "cpi" in daily.columns else "SPI Trend (S-Curve)"
    fig_sc.update_layout(title=dict(text=trend_title,font=dict(color="#8aa2c0",size=12)),
        height=260,xaxis_title="Date",yaxis_title="Index Value")
    st.plotly_chart(dark_fig(fig_sc),use_container_width=True,config={"displayModeBar":False})
elif date_col and "earned_value" in schedule_df.columns and "planned_value" in schedule_df.columns:
    sd=schedule_df.copy()
    sd["_date"]=pd.to_datetime(sd[date_col],errors="coerce")
    sd=sd.dropna(subset=["_date"]).sort_values("_date")
    sd["cum_pv"]=sd["planned_value"].cumsum()
    sd["cum_ev"]=sd["earned_value"].cumsum()
    sd["cum_ac"]=sd["actual_cost"].cumsum() if "actual_cost" in sd.columns else 0
    fig_sc=go.Figure()
    fig_sc.add_trace(go.Scatter(x=sd["_date"],y=sd["cum_pv"],name="Cumulative PV",
        line=dict(color=BLUE,width=2.5,dash="dash"),fill="tozeroy",fillcolor="rgba(0,160,255,.06)"))
    fig_sc.add_trace(go.Scatter(x=sd["_date"],y=sd["cum_ev"],name="Cumulative EV",
        line=dict(color=GREEN,width=2.5),fill="tozeroy",fillcolor="rgba(0,255,136,.06)"))
    fig_sc.add_trace(go.Scatter(x=sd["_date"],y=sd["cum_ac"],name="Cumulative AC",
        line=dict(color=PINK,width=2.5)))
    fig_sc.update_layout(title=dict(text="Cumulative PV vs EV vs AC (S-Curve)",font=dict(color="#8aa2c0",size=12)),
        height=280,xaxis_title="Date",yaxis_title="KES")
    st.plotly_chart(dark_fig(fig_sc),use_container_width=True,config={"displayModeBar":False})
else:
    st.info("S-Curve requires schedule date columns and either SPI history records or PV/EV data with dates.")
st.markdown("</div>",unsafe_allow_html=True)
st.markdown("<div style='height:14px'></div>",unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════
#  NEW — SPI TREND HISTORY  (Objective 4: proactive detection)
# ════════════════════════════════════════════════════════════
st.markdown('<div class="card">',unsafe_allow_html=True)
st.markdown('<div class="section-header">🔭 SPI Trend Analysis — Early Warning</div>',unsafe_allow_html=True)

required_spi_cols={"task_id","recorded_at","spi"}
has_spi_history=(not spi_hist_df.empty) and required_spi_cols.issubset(spi_hist_df.columns)

if has_spi_history:
    sh2=spi_hist_df.loc[:,["task_id","recorded_at","spi"]].copy()
    sh2["task_id"]=sh2["task_id"].astype(str).str.strip()
    sh2["recorded_at"]=pd.to_datetime(sh2["recorded_at"],errors="coerce")
    sh2["spi"]=pd.to_numeric(sh2["spi"],errors="coerce")
    sh2=sh2.replace([np.inf,-np.inf],np.nan).dropna(subset=["task_id","recorded_at","spi"])
    sh2=sh2[sh2["task_id"]!=""]
    sh2["spi"]=sh2["spi"].clip(lower=0,upper=3.0)

    if not sh2.empty:
        sh2["period"]=sh2["recorded_at"].dt.floor("D")
        trend_daily=(sh2.groupby(["task_id","period"],as_index=False)["spi"]
                       .mean()
                       .rename(columns={"period":"recorded_at"}))
        trend_daily=trend_daily.sort_values(["task_id","recorded_at"])

        latest=trend_daily.groupby("task_id",as_index=False).tail(1).copy()
        previous=trend_daily.groupby("task_id",as_index=False).nth(-2).reset_index(drop=True)
        previous=previous.rename(columns={"spi":"previous_spi"})[["task_id","previous_spi"]]
        samples=trend_daily.groupby("task_id",as_index=False).size().rename(columns={"size":"samples"})
        latest=latest.merge(previous,on="task_id",how="left").merge(samples,on="task_id",how="left")
        latest["delta"]=latest["spi"]-latest["previous_spi"]
        latest["is_critical"]=latest["spi"]<1.0
        latest["is_warning"]=(latest["spi"]>=1.0)&(latest["spi"]<spi_warn_thresh)
        latest["is_declining"]=latest["delta"].lt(-0.01).fillna(False)
        latest["risk_score"]=(
            latest["is_critical"].astype(int)*3+
            latest["is_warning"].astype(int)*2+
            latest["is_declining"].astype(int)
        )
        latest=latest.sort_values(["risk_score","spi","delta"],ascending=[False,True,True])
        top_tasks=latest.head(8)["task_id"].tolist()

        fig_trend=go.Figure()
        for i,tid in enumerate(top_tasks):
            sub=trend_daily[trend_daily["task_id"]==tid]
            row=latest[latest["task_id"]==tid].iloc[0]
            lcolor=RED if row["is_critical"] else (AMBER if row["is_declining"] or row["is_warning"] else RING[i%len(RING)])
            fig_trend.add_trace(go.Scatter(
                x=sub["recorded_at"],y=sub["spi"],name=str(tid),
                line=dict(color=lcolor,width=2.2),mode="lines+markers",
                marker=dict(size=5,color=lcolor),
                hovertemplate="<b>%{fullData.name}</b><br>Date: %{x|%Y-%m-%d}<br>SPI: %{y:.3f}<extra></extra>"))

        fig_trend.add_hline(y=1.0,line_dash="dot",line_color=GREEN,line_width=1,
                            annotation_text="Target 1.0",annotation_font_color=GREEN,annotation_font_size=9)
        fig_trend.add_hline(y=spi_warn_thresh,line_dash="dot",line_color=AMBER,line_width=1,
                            annotation_text=f"Warning {spi_warn_thresh:.2f}",annotation_font_color=AMBER,annotation_font_size=9)
        fig_trend.update_layout(
            title=dict(text="Highest-risk task SPI trends",font=dict(color="#8aa2c0",size=12)),
            height=320,xaxis_title="Date",yaxis_title="SPI",
            legend=dict(orientation="h",yanchor="bottom",y=1.02,xanchor="right",x=1))
        st.plotly_chart(dark_fig(fig_trend),use_container_width=True,config={"displayModeBar":False})

        critical_tasks=latest[latest["is_critical"]]["task_id"].astype(str).head(8).tolist()
        early_tasks=latest[(~latest["is_critical"])&(latest["is_declining"]|latest["is_warning"])]["task_id"].astype(str).head(8).tolist()

        a1,a2,a3=st.columns(3,gap="small")
        with a1:
            if critical_tasks:
                st.markdown(f'<div class="alert-red"><div style="color:{RED};font-size:.78rem;font-weight:700">🚨 SPI Below 1.0</div>'
                            f'<div style="color:#e2eaff;font-size:.74rem;margin-top:3px">{", ".join(critical_tasks)}</div></div>',unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="alert-green"><div style="color:{GREEN};font-size:.78rem;font-weight:700">✅ No Critical SPI Tasks</div></div>',unsafe_allow_html=True)
        with a2:
            if early_tasks:
                st.markdown(f'<div class="alert-amber"><div style="color:{AMBER};font-size:.78rem;font-weight:700">⚠️ Early Warning</div>'
                            f'<div style="color:#e2eaff;font-size:.74rem;margin-top:3px">{", ".join(early_tasks)}</div></div>',unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="alert-green"><div style="color:{GREEN};font-size:.78rem;font-weight:700">✅ No Warning Trends</div></div>',unsafe_allow_html=True)
        with a3:
            st.markdown(f'<div style="background:rgba(0,160,255,.07);border:1px solid rgba(0,160,255,.18);border-radius:14px;padding:.7rem">'
                        f'<div class="label">History Points</div><div class="med-val" style="color:{BLUE}">{len(trend_daily)}</div>'
                        f'<div style="color:#5a6a8a;font-size:.68rem;margin-top:3px">{trend_daily["task_id"].nunique()} tasks tracked</div></div>',unsafe_allow_html=True)

        risk_table=latest[["task_id","spi","previous_spi","delta","samples"]].head(8).copy()
        risk_table.columns=["Task ID","Latest SPI","Previous SPI","Change","Samples"]
        st.dataframe(risk_table.style.format({"Latest SPI":"{:.3f}","Previous SPI":"{:.3f}","Change":"{:+.3f}"}),
                     use_container_width=True,height=250)
    else:
        st.info("SPI history was found, but none of the records had valid task IDs, dates, and SPI values.")
else:
    current_spi=filtered[["task_id","SPI"]].copy() if {"task_id","SPI"}.issubset(filtered.columns) else pd.DataFrame()
    if not current_spi.empty:
        current_spi=(current_spi.groupby("task_id",as_index=False)["SPI"].mean()
                     .sort_values("SPI",ascending=True).head(10))
        fig_current=px.bar(current_spi,x="task_id",y="SPI",
                           title="Current lowest SPI tasks (snapshot only)",
                           color="SPI",color_continuous_scale=[RED,AMBER,GREEN],
                           range_color=[0,max(1.2,float(current_spi["SPI"].max()))])
        fig_current.add_hline(y=1.0,line_dash="dot",line_color=GREEN,
                              annotation_text="Target 1.0",annotation_font_color=GREEN,annotation_font_size=9)
        fig_current.update_layout(height=280,xaxis_title="Task ID",yaxis_title="Current SPI",
                                  coloraxis_showscale=False)
        st.plotly_chart(dark_fig(fig_current),use_container_width=True,config={"displayModeBar":False})
    st.info("No usable SPI history yet. Run the sync process on at least two different dates to turn this snapshot into a true trend.")
st.markdown("</div>",unsafe_allow_html=True)
st.markdown("<div style='height:14px'></div>",unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════
#  NEW — INTEGRATION HEALTH PANEL  (Objective 1 & 2)
# ════════════════════════════════════════════════════════════
st.markdown('<div class="card">',unsafe_allow_html=True)
st.markdown('<div class="section-header">🔗 BIM–Schedule Integration Health</div>',unsafe_allow_html=True)

ih1,ih2=st.columns([1,2],gap="small")
with ih1:
    mr_color=GREEN if match_rate>=90 else (AMBER if match_rate>=70 else RED)
    st.markdown(f"""
    <div style="display:flex;flex-direction:column;gap:.7rem">
      <div style="background:rgba(0,160,255,.08);border:1px solid rgba(0,160,255,.2);border-radius:14px;padding:.85rem">
        <div class="label">Match Rate</div>
        <div class="big-val" style="color:{mr_color}">{match_rate:.1f}<span class="sub">%</span></div>
        <div class="pbar-wrap" style="margin-top:8px">
          <div style="height:100%;border-radius:999px;width:{match_rate:.1f}%;background:{mr_color}"></div>
        </div>
      </div>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:.6rem">
        <div style="background:rgba(0,255,136,.07);border:1px solid rgba(0,255,136,.15);border-radius:12px;padding:.65rem">
          <div class="label">Matched</div>
          <div class="med-val" style="color:{GREEN}">{len(matched_tids)}</div>
        </div>
        <div style="background:rgba(255,107,107,.07);border:1px solid rgba(255,107,107,.15);border-radius:12px;padding:.65rem">
          <div class="label">Orphaned</div>
          <div class="med-val" style="color:{RED}">{len(revit_only_tids)}</div>
        </div>
        <div style="background:rgba(255,183,0,.07);border:1px solid rgba(255,183,0,.15);border-radius:12px;padding:.65rem">
          <div class="label">Revit Only</div>
          <div class="med-val" style="color:{AMBER}">{len(revit_only_tids)}</div>
        </div>
        <div style="background:rgba(168,85,247,.07);border:1px solid rgba(168,85,247,.15);border-radius:12px;padding:.65rem">
          <div class="label">Sched Only</div>
          <div class="med-val" style="color:{PURPLE}">{len(sched_only_tids)}</div>
        </div>
      </div>
    </div>""",unsafe_allow_html=True)

with ih2:
    # BIM-Schedule Linkage Table (NEW — Objective 2)
    st.markdown('<div style="font-size:.76rem;color:#5a6a8a;text-transform:uppercase;letter-spacing:1px;margin-bottom:.5rem">Task ID Linkage Table</div>',unsafe_allow_html=True)
    link_rows=[]
    for tid in sorted(all_revit_tids|all_sched_tids):
        in_revit=tid in all_revit_tids
        in_sched=tid in all_sched_tids
        cat_list=list(elements_df[elements_df["task_id"]==tid]["category"].unique()) if in_revit else []
        cat_str=cat_list[0] if cat_list else "—"
        n_elems=len(elements_df[elements_df["task_id"]==tid]) if in_revit else 0
        task_name=schedule_df[schedule_df["task_id"]==tid]["task_name"].values[0] \
                  if in_sched and "task_name" in schedule_df.columns else "—"
        if len(task_name)>30: task_name=task_name[:28]+"…"
        if in_revit and in_sched: status="✅ Linked"
        elif in_revit: status="⚠️ No Schedule"
        else: status="⚠️ No Revit"
        link_rows.append({"Task ID":tid,"Category":cat_str,"Elements":n_elems,
                          "Task Name":task_name,"Status":status})
    if link_rows:
        link_df=pd.DataFrame(link_rows)
        def hl_status(v):
            if "Linked" in str(v): return "color:#00ff88;font-weight:600"
            return "color:#ffb700;font-weight:600"
        st.dataframe(link_df.style.map(hl_status,subset=["Status"]),
                     use_container_width=True,height=280)
    else:
        st.info("No elements or schedule tasks found.")

# Orphan warnings
if revit_only_tids:
    st.markdown(f'<div class="alert-amber" style="margin-top:.8rem">'
                f'<div style="color:{AMBER};font-size:.76rem;font-weight:700">⚠️ {len(revit_only_tids)} Revit elements have no schedule task — excluded from EVM</div>'
                f'<div style="color:#e2eaff;font-size:.7rem;margin-top:3px">{", ".join(sorted(revit_only_tids)[:10])}'
                f'{"…" if len(revit_only_tids)>10 else ""}</div></div>',unsafe_allow_html=True)
if sched_only_tids:
    st.markdown(f'<div class="alert-amber" style="margin-top:.5rem">'
                f'<div style="color:{AMBER};font-size:.76rem;font-weight:700">⚠️ {len(sched_only_tids)} schedule tasks have no Revit element</div>'
                f'<div style="color:#e2eaff;font-size:.7rem;margin-top:3px">{", ".join(sorted(sched_only_tids)[:10])}'
                f'{"…" if len(sched_only_tids)>10 else ""}</div></div>',unsafe_allow_html=True)

st.markdown("</div>",unsafe_allow_html=True)
st.markdown("<div style='height:14px'></div>",unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════
#  NEW — BIM COST vs EVM COST  (Objective 3: 5D dimension)
# ════════════════════════════════════════════════════════════
st.markdown('<div class="card">',unsafe_allow_html=True)
st.markdown('<div class="section-header">💰 BIM-Derived Cost vs EVM Actual Cost — 5D Comparison</div>',unsafe_allow_html=True)

bv1,bv2,bv3=st.columns(3,gap="small")
bim_vs_ac=total_bim_cost-total_ac
with bv1:
    st.markdown(f"""
    <div style="background:rgba(0,160,255,.07);border:1px solid rgba(0,160,255,.2);
                border-radius:14px;padding:.9rem;text-align:center">
      <div class="label">BIM Estimated Cost</div>
      <div class="med-val" style="color:{BLUE}">{fmt(total_bim_cost)} KES</div>
      <div style="font-size:.65rem;color:#5a6a8a;margin-top:3px">From Revit quantities × unit rates</div>
    </div>""",unsafe_allow_html=True)
with bv2:
    st.markdown(f"""
    <div style="background:rgba(255,61,154,.07);border:1px solid rgba(255,61,154,.2);
                border-radius:14px;padding:.9rem;text-align:center">
      <div class="label">EVM Actual Cost</div>
      <div class="med-val" style="color:{PINK}">{fmt(total_ac)} KES</div>
      <div style="font-size:.65rem;color:#5a6a8a;margin-top:3px">From MS Project tracking</div>
    </div>""",unsafe_allow_html=True)
with bv3:
    bvc=GREEN if bim_vs_ac>=0 else RED
    st.markdown(f"""
    <div style="background:rgba(0,255,136,.07);border:1px solid rgba(0,255,136,.2);
                border-radius:14px;padding:.9rem;text-align:center">
      <div class="label">BIM vs EVM Variance</div>
      <div class="med-val" style="color:{bvc}">{signed(bim_vs_ac)} KES</div>
      <div style="font-size:.65rem;color:#5a6a8a;margin-top:3px">
        {'BIM estimate exceeds actual' if bim_vs_ac>=0 else 'Actual exceeds BIM estimate'}</div>
    </div>""",unsafe_allow_html=True)

if "total_cost" in filtered.columns and "actual_cost" in filtered.columns:
    cat_comp=filtered.groupby("category").agg({"total_cost":"sum","actual_cost":"sum"}).reset_index()
    fig_comp=go.Figure()
    fig_comp.add_trace(go.Bar(name="BIM Estimated",x=cat_comp["category"],y=cat_comp["total_cost"],
                              marker_color=BLUE,opacity=0.85))
    fig_comp.add_trace(go.Bar(name="EVM Actual Cost",x=cat_comp["category"],y=cat_comp["actual_cost"],
                              marker_color=PINK,opacity=0.85))
    fig_comp.update_layout(barmode="group",
        title=dict(text="BIM Cost Estimate vs EVM Actual by Category",font=dict(color="#8aa2c0",size=12)),
        height=250)
    st.plotly_chart(dark_fig(fig_comp),use_container_width=True,config={"displayModeBar":False})

st.markdown("</div>",unsafe_allow_html=True)
st.markdown("<div style='height:14px'></div>",unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════
#  ROW — COST PIE + DELAY INTELLIGENCE
# ════════════════════════════════════════════════════════════
r4c1,r4c2=st.columns([1,1],gap="small")

with r4c1:
    fig_pie=go.Figure(go.Pie(labels=cost_by_cat["category"],values=cost_by_cat["total_cost"],hole=0.5,
        marker=dict(colors=RING[:len(cost_by_cat)],line=dict(color="#090b0f",width=2)),
        textinfo="percent",textfont=dict(size=9,color="#eef4ff"),
        hovertemplate="<b>%{label}</b><br>%{value:,.0f} KES<extra></extra>"))
    fig_pie.update_layout(title=dict(text="Cost Breakdown by Category",font=dict(color="#8aa2c0",size=12)),
        height=290,legend=dict(bgcolor="rgba(0,0,0,0)",font=dict(color="#5a6a8a",size=9)),
        margin=dict(l=0,r=10,t=38,b=0),paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)")
    st.markdown('<div class="card">',unsafe_allow_html=True)
    st.plotly_chart(fig_pie,use_container_width=True,config={"displayModeBar":False})
    st.markdown("</div>",unsafe_allow_html=True)

with r4c2:
    st.markdown('<div class="card" style="height:100%">',unsafe_allow_html=True)
    st.markdown('<div class="section-header">🔮 Delay Intelligence</div>',unsafe_allow_html=True)
    if not spi_hist_df.empty:
        spi_hist_df["recorded_at"]=pd.to_datetime(spi_hist_df["recorded_at"])
        dec=[]
        for tid,grp in spi_hist_df.groupby("task_id"):
            sp=grp.sort_values("recorded_at")["spi"].values
            if len(sp)>=3 and sp[-3]>sp[-2]>sp[-1]: dec.append(tid)
        if dec:
            st.markdown(f'<div class="alert-red"><div style="color:{RED};font-size:.78rem;font-weight:700">⚠️ SPI Declining 3 Periods</div>'
                        f'<div style="color:#e2eaff;font-size:.74rem;margin-top:3px">{", ".join(dec)}</div></div>',unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="alert-green"><div style="color:{GREEN};font-size:.78rem;font-weight:700">✅ No Sustained Declining Trends</div></div>',unsafe_allow_html=True)
    else:
        st.markdown('<div style="color:#5a6a8a;font-size:.74rem">Run sync tool 3+ times to enable trend analysis</div>',unsafe_allow_html=True)
    st.markdown(f"""
    <div class="div"></div>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:.65rem">
      <div style="background:rgba(255,107,107,.07);border:1px solid rgba(255,107,107,.15);border-radius:12px;padding:.7rem">
        <div class="label">Delayed</div><div class="med-val" style="color:{RED}">{delayed_count}</div></div>
      <div style="background:rgba(255,183,0,.07);border:1px solid rgba(255,183,0,.15);border-radius:12px;padding:.7rem">
        <div class="label">Over Budget</div><div class="med-val" style="color:{AMBER}">{overbudget_count}</div></div>
      <div style="background:rgba(0,255,136,.07);border:1px solid rgba(0,255,136,.15);border-radius:12px;padding:.7rem">
        <div class="label">On Track</div><div class="med-val" style="color:{GREEN}">{on_track}</div></div>
      <div style="background:rgba(0,160,255,.07);border:1px solid rgba(0,160,255,.15);border-radius:12px;padding:.7rem">
        <div class="label">TCPI</div><div class="med-val" style="color:{tcpi_col}">{TCPI:.3f}</div></div>
    </div>""",unsafe_allow_html=True)
    st.markdown("</div>",unsafe_allow_html=True)

st.markdown("<div style='height:14px'></div>",unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════
#  MONTE CARLO  (FIX: real duration baseline)
# ════════════════════════════════════════════════════════════
st.markdown('<div class="card">',unsafe_allow_html=True)
st.markdown('<div class="section-header">🎲 Monte Carlo Simulation</div>',unsafe_allow_html=True)
spi_vals=filtered["SPI"].replace(0,np.nan).dropna()
sim_dur=p50=p80=p90=None
if len(spi_vals)>=2:
    num_sim=st.slider("Simulations",100,2000,500,step=100)
    sim_spi=np.random.choice(spi_vals,size=(num_sim,len(spi_vals)),replace=True)
    # FIX 8 — use real project duration, not hardcoded 100
    sim_dur=planned_duration/sim_spi.mean(axis=1)
    p50,p80,p90=np.percentile(sim_dur,[50,80,90])
    mc1,mc2=st.columns([3,1],gap="small")
    with mc1:
        fig_mc=px.histogram(sim_dur,nbins=50,color_discrete_sequence=[BLUE],opacity=0.8)
        fig_mc.add_vline(x=planned_duration,line_dash="dot",line_color=GREEN,line_width=1.5,
            annotation_text=f"Baseline {planned_duration}d",annotation_font_color=GREEN,annotation_font_size=9)
        fig_mc.add_vline(x=p80,line_dash="dash",line_color=PINK,line_width=1.5,
            annotation_text=f"P80={p80:.0f}d",annotation_font_color=PINK,annotation_font_size=9)
        fig_mc.update_layout(title=dict(text=f"Simulated Duration (planned={planned_duration}d from schedule)",
            font=dict(color="#8aa2c0",size=12)),showlegend=False,height=230,
            xaxis_title="Duration (days)",yaxis_title="Frequency")
        st.plotly_chart(dark_fig(fig_mc),use_container_width=True,config={"displayModeBar":False})
    with mc2:
        st.markdown(f"""
        <div style="display:flex;flex-direction:column;gap:.6rem;padding-top:.3rem">
          <div style="background:rgba(0,255,136,.08);border:1px solid rgba(0,255,136,.2);border-radius:12px;padding:.7rem">
            <div class="label">P50</div><div class="med-val" style="color:{GREEN}">{p50:.0f}<span class="sub">d</span></div></div>
          <div style="background:rgba(255,61,154,.08);border:1px solid rgba(255,61,154,.2);border-radius:12px;padding:.7rem">
            <div class="label">P80</div><div class="med-val" style="color:{PINK}">{p80:.0f}<span class="sub">d</span></div></div>
          <div style="background:rgba(255,183,0,.08);border:1px solid rgba(255,183,0,.2);border-radius:12px;padding:.7rem">
            <div class="label">P90</div><div class="med-val" style="color:{AMBER}">{p90:.0f}<span class="sub">d</span></div></div>
        </div>""",unsafe_allow_html=True)
else:
    st.info("Need ≥2 tasks with valid SPI values to run Monte Carlo.")
st.markdown("</div>",unsafe_allow_html=True)
st.markdown("<div style='height:14px'></div>",unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════
#  GANTT CHART  (Objective 4 — new addition)
# ════════════════════════════════════════════════════════════
st.markdown('<div class="card">',unsafe_allow_html=True)
st.markdown('<div class="section-header">📅 Project Gantt Schedule</div>',unsafe_allow_html=True)
sc_col=next((c for c in ["start_date","planned_start"] if c in schedule_df.columns),None)
fc_col=next((c for c in ["finish_date","planned_finish"] if c in schedule_df.columns),None)
if sc_col and fc_col:
    sg=schedule_df.copy()
    sg["_s"]=pd.to_datetime(sg[sc_col],errors="coerce")
    sg["_f"]=pd.to_datetime(sg[fc_col],errors="coerce")
    sg=sg.dropna(subset=["_s","_f"])
    if not sg.empty:
        fig_g=go.Figure()
        for _,row in sg.iterrows():
            spi_val=merged[merged["task_id"]==row["task_id"]]["SPI"].mean() if row["task_id"] in merged["task_id"].values else 1.0
            bar_color=RED if spi_val<1.0 else (AMBER if spi_val<(spi_warn_thresh+0.05) else GREEN)
            fig_g.add_trace(go.Bar(
                x=[(row["_f"]-row["_s"]).days],base=[row["_s"]],
                y=[str(row.get("task_id",""))],orientation="h",
                marker_color=bar_color,opacity=0.8,
                name=str(row.get("task_id","")),showlegend=False,
                hovertemplate=f"<b>{row.get('task_id','')}</b><br>"
                              f"Start: {row['_s'].strftime('%Y-%m-%d')}<br>"
                              f"Finish: {row['_f'].strftime('%Y-%m-%d')}<extra></extra>"))
        fig_g.update_layout(barmode="overlay",
            title=dict(text="Schedule (green=on track, amber=warning, red=delayed)",
                       font=dict(color="#8aa2c0",size=12)),
            height=max(300,len(sg)*28),xaxis=dict(type="date"),
            yaxis=dict(title="Task ID",tickfont=dict(size=9)))
        st.plotly_chart(dark_fig(fig_g),use_container_width=True,config={"displayModeBar":False})
    else:
        st.info("No valid date ranges for Gantt chart.")
else:
    st.info("Schedule needs start_date/planned_start and finish_date/planned_finish columns.")
st.markdown("</div>",unsafe_allow_html=True)
st.markdown("<div style='height:14px'></div>",unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════
#  RISK HEATMAP
# ════════════════════════════════════════════════════════════
st.markdown('<div class="card">',unsafe_allow_html=True)
st.markdown('<div class="section-header">⚠️ Risk Heatmap</div>',unsafe_allow_html=True)
heat_df=filtered[["task_id","category","SPI","CPI","Delayed","OverBudget"]].copy()
heat_df["SPI"]=heat_df["SPI"].map("{:.3f}".format)
heat_df["CPI"]=heat_df["CPI"].map("{:.3f}".format)
def cr(v):
    try:
        x=float(v)
        if x<0.8:  return "background-color:#3d0f0f;color:#ff6b6b"
        if x<spi_warn_thresh: return "background-color:#3d2e0f;color:#ffb700"
        return "background-color:#0f2e1a;color:#00ff88"
    except: return ""
st.dataframe(heat_df.style.map(cr,subset=["SPI","CPI"]),use_container_width=True,height=290)
st.markdown("</div>",unsafe_allow_html=True)
st.markdown("<div style='height:14px'></div>",unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════
#  PHOTOS + COMMENTS
# ════════════════════════════════════════════════════════════
ph_col,cm_col=st.columns([1,1],gap="small")

with ph_col:
    st.markdown('<div class="card">',unsafe_allow_html=True)
    st.markdown('<div class="section-header">📸 Site Photos</div>',unsafe_allow_html=True)
    up=st.file_uploader("Upload site photo",type=["jpg","jpeg","png"],key="photo_up")
    if up:
        try:
            import uuid
            fb=up.getvalue(); ext=up.name.split(".")[-1]
            fn=f"photo_{uuid.uuid4().hex[:8]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{ext}"
            supabase.storage.from_("photos").upload(fn,fb)
            url=supabase.storage.from_("photos").get_public_url(fn)
            supabase.table("photos").insert({"project_id":project_id,"task_id":None,
                "file_path":url,"caption":"Uploaded","uploaded_by":"Dashboard",
                "completion_status":"Not Started"}).execute()
            st.success("Photo uploaded!"); st.rerun()
        except Exception as e: st.error(f"Upload failed: {e}")
    if not photos_df.empty:
        pc=st.columns(2)
        for idx,(_,row) in enumerate(photos_df.head(6).iterrows()):
            with pc[idx%2]:
                st.image(row["file_path"],caption=row.get("caption",""),use_container_width=True)
                if row.get("task_id"):
                    prg=schedule_df[schedule_df["task_id"]==row["task_id"]]["percent_complete"].values
                    pv=min(prg[0]/100,1.0) if len(prg) else 0
                    st.markdown(f'<div style="font-size:.65rem;color:#5a6a8a">{row["task_id"]} — {pv*100:.0f}%</div>'
                                f'{pbar(pv)}',unsafe_allow_html=True)
    else:
        st.markdown('<div style="color:#3a4a62;font-size:.76rem;padding:.4rem">No photos yet.</div>',unsafe_allow_html=True)
    st.markdown("</div>",unsafe_allow_html=True)

with cm_col:
    st.markdown('<div class="card">',unsafe_allow_html=True)
    st.markdown('<div class="section-header">💬 Comments</div>',unsafe_allow_html=True)
    for _,row in comments_df.head(10).iterrows():
        # FIX 9 — html.escape prevents XSS
        eu=html.escape(str(row.get("user_name",""))); ec=html.escape(str(row.get("comment","")))
        ts=str(row.get("created_at",""))[:16]
        if row.get("is_emergency"):
            st.markdown(f'<div class="comment-emg"><div style="color:{RED};font-size:.68rem;font-weight:700">🚨 {eu}</div>'
                        f'<div style="color:#e2eaff;font-size:.74rem;margin-top:2px">{ec}</div>'
                        f'<div style="color:#5a6a8a;font-size:.6rem;margin-top:3px">{ts}</div></div>',unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="comment-norm"><div style="color:#6ab4ff;font-size:.68rem;font-weight:700">{eu}</div>'
                        f'<div style="color:#b0c4e0;font-size:.74rem;margin-top:2px">{ec}</div>'
                        f'<div style="color:#5a6a8a;font-size:.6rem;margin-top:3px">{ts}</div></div>',unsafe_allow_html=True)
    st.markdown('<div class="div"></div>',unsafe_allow_html=True)
    with st.form("comment_form",clear_on_submit=True):
        user=st.text_input("Your name","Anonymous")
        comment=st.text_area("Comment",height=70)
        is_emg=st.checkbox("🚨 Emergency")
        if st.form_submit_button("Post Comment"):
            if not comment.strip(): st.warning("Comment cannot be empty.")
            else:
                supabase.table("comments").insert({"project_id":project_id,"user_name":user,
                    "comment":comment,"is_emergency":int(is_emg),
                    "created_at":datetime.now().isoformat()}).execute()
                st.rerun()
    st.markdown("</div>",unsafe_allow_html=True)

st.markdown("<div style='height:14px'></div>",unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════
#  PDF EXPORT — professional white A4
# ════════════════════════════════════════════════════════════
st.markdown('<div class="card">',unsafe_allow_html=True)
st.markdown('<div class="section-header">📄 Export Report</div>',unsafe_allow_html=True)

if st.button("📄 Generate PDF Report"):
    buf=io.BytesIO()
    doc=SimpleDocTemplate(buf,pagesize=A4,
        leftMargin=2*cm,rightMargin=2*cm,topMargin=2*cm,bottomMargin=2*cm)
    styles=getSampleStyleSheet()
    BB=rl_colors.HexColor("#1a3a6b"); BD=rl_colors.HexColor("#0d1a2e")
    AT=rl_colors.HexColor("#007aaa"); RA=rl_colors.HexColor("#f0f4f8")

    S=lambda n,**kw: ParagraphStyle(n,**kw)
    s_ttl =S("t",fontSize=22,textColor=BD,fontName="Helvetica-Bold",spaceAfter=4)
    s_prj =S("p",fontSize=14,textColor=BB,fontName="Helvetica-Bold",spaceAfter=2)
    s_cap =S("c",fontSize=8, textColor=rl_colors.HexColor("#4a6080"),fontName="Helvetica-Oblique",spaceAfter=2)
    s_sec =S("s",fontSize=13,textColor=BB,fontName="Helvetica-Bold",spaceBefore=14,spaceAfter=6)
    s_ftr =S("f",fontSize=8, textColor=rl_colors.HexColor("#8090a0"),fontName="Helvetica",alignment=TA_CENTER)

    def mk_ts(hc=BB):
        return TableStyle([
            ("BACKGROUND",(0,0),(-1,0),hc),("TEXTCOLOR",(0,0),(-1,0),rl_colors.white),
            ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),("FONTSIZE",(0,0),(-1,0),9),
            ("FONTNAME",(0,1),(-1,-1),"Helvetica"),("FONTSIZE",(0,1),(-1,-1),9),
            ("TEXTCOLOR",(0,1),(-1,-1),BD),("ROWBACKGROUNDS",(0,1),(-1,-1),[rl_colors.white,RA]),
            ("GRID",(0,0),(-1,-1),0.4,rl_colors.HexColor("#c8d4e0")),
            ("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5),
            ("LEFTPADDING",(0,0),(-1,-1),7),("RIGHTPADDING",(0,0),(-1,-1),7)])

    story=[]
    story.append(Paragraph("5D BIM Construction Report",s_ttl))
    story.append(Paragraph(selected_project,s_prj))
    story.append(Paragraph(f"Generated: {datetime.now().strftime('%d %B %Y, %H:%M')}  |  Sync: {today_str}",s_cap))
    story.append(HRFlowable(width="100%",thickness=2,color=BB,spaceAfter=10))

    # Executive summary
    story.append(Paragraph("Executive Summary",s_sec))
    sd=[["Metric","Value","Metric","Value"],
        ["Planned Value",f"{total_pv:,.0f} KES","Earned Value",f"{total_ev:,.0f} KES"],
        ["Actual Cost",f"{total_ac:,.0f} KES","BIM Est. Cost",f"{total_bim_cost:,.0f} KES"],
        ["SPI",f"{overall_spi:.3f}","CPI",f"{overall_cpi:.3f}"],
        ["EAC",f"{EAC:,.0f} KES","ETC",f"{ETC:,.0f} KES"],
        ["TCPI",f"{TCPI:.3f}","Progress",f"{overall_prog*100:.1f}%"],
        ["Cost Variance",f"{vc:,.0f} KES","Sched Variance",f"{vs:,.0f} KES"],
        ["On Track",str(on_track),"Delayed",str(delayed_count)],
        ["Over Budget",str(overbudget_count),"Match Rate",f"{match_rate:.1f}%"]]
    t=Table(sd,colWidths=[4*cm,5*cm,4*cm,5*cm],repeatRows=1)
    t.setStyle(mk_ts()); story.append(t); story.append(Spacer(1,10))

    # Integration health
    story.append(Paragraph("BIM–Schedule Integration Health",s_sec))
    ih=[["Metric","Value","Status"],
        ["Total Revit Task IDs",str(len(all_revit_tids)),"—"],
        ["Matched to Schedule",str(len(matched_tids)),
         "Good" if match_rate>=90 else ("Acceptable" if match_rate>=70 else "Needs Attention")],
        ["Revit-Only (no schedule)",str(len(revit_only_tids)),
         "OK" if len(revit_only_tids)==0 else "Fix Required"],
        ["Schedule-Only (no Revit)",str(len(sched_only_tids)),
         "OK" if len(sched_only_tids)==0 else "Fix Required"],
        ["Match Rate",f"{match_rate:.1f}%",
         "✓ Good" if match_rate>=90 else ("▲ Acceptable" if match_rate>=70 else "✗ Poor")]]
    ti=Table(ih,colWidths=[7*cm,4*cm,7*cm],repeatRows=1)
    ti.setStyle(mk_ts(AT)); story.append(ti); story.append(Spacer(1,10))

    # Category breakdown
    story.append(Paragraph("Cost Breakdown by Category",s_sec))
    cat_sum=filtered.groupby("category").agg({"total_cost":"sum","planned_value":"sum",
        "actual_cost":"sum","SPI":"mean","CPI":"mean"}).reset_index().sort_values("total_cost",ascending=False)
    cd=[["Category","BIM Cost","Planned","Actual","SPI","CPI","Status"]]
    for _,row in cat_sum.iterrows():
        cd.append([row["category"],f"{row['total_cost']:,.0f}",f"{row['planned_value']:,.0f}",
            f"{row['actual_cost']:,.0f}",f"{row['SPI']:.3f}",f"{row['CPI']:.3f}",
            "On Track" if row["SPI"]>=1.0 else "Delayed"])
    tc=Table(cd,colWidths=[3*cm,2.8*cm,2.8*cm,2.8*cm,1.7*cm,1.7*cm,2.2*cm],repeatRows=1)
    ts_c=mk_ts()
    for i,(_,row) in enumerate(cat_sum.iterrows(),start=1):
        c_=rl_colors.HexColor("#1a7a3a") if row["SPI"]>=1.0 else rl_colors.HexColor("#b00020")
        ts_c.add("TEXTCOLOR",(6,i),(6,i),c_); ts_c.add("FONTNAME",(6,i),(6,i),"Helvetica-Bold")
    tc.setStyle(ts_c); story.append(tc); story.append(Spacer(1,10))

    # EVM analysis
    story.append(Paragraph("EVM Performance Analysis",s_sec))
    spi_s="On Schedule" if overall_spi>=1.0 else f"Behind — gap {(1-overall_spi)*100:.1f}%"
    cpi_s="Under Budget" if overall_cpi>=1.0 else f"Over Budget — {(1-overall_cpi)*100:.1f}%"
    tcpi_s="Achievable" if TCPI<=1.1 else ("Challenging" if TCPI<=1.25 else "Unlikely — re-baseline")
    ev=[["Indicator","Value","Interpretation"],
        ["SPI",f"{overall_spi:.3f}",spi_s],["CPI",f"{overall_cpi:.3f}",cpi_s],
        ["EAC",f"{EAC:,.0f} KES",f"{'Within' if EAC<=total_pv else 'Exceeds'} budget by {abs(EAC-total_pv):,.0f}"],
        ["TCPI",f"{TCPI:.3f}",tcpi_s]]
    te=Table(ev,colWidths=[4.5*cm,3.5*cm,9.8*cm],repeatRows=1)
    te.setStyle(mk_ts(AT)); story.append(te); story.append(Spacer(1,16))

    story.append(HRFlowable(width="100%",thickness=1,color=rl_colors.HexColor("#c8d4e0")))
    story.append(Spacer(1,4))
    story.append(Paragraph(f"Confidential · {selected_project} · 5D BIM Framework · {today_str}",s_ftr))

    doc.build(story)
    st.download_button("⬇️ Download PDF Report",buf.getvalue(),
        file_name=f"bim_{selected_project.replace(' ','_')}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
        mime="application/pdf")

st.markdown("</div>",unsafe_allow_html=True)
st.markdown("<div style='height:14px'></div>",unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════
#  ADVANCED CONTROLS  (bottom)
# ════════════════════════════════════════════════════════════
st.markdown('<div style="font-size:.74rem;font-weight:700;text-transform:uppercase;'
            'letter-spacing:2px;color:#2e3d50;padding:0 .2rem .5rem">⚙️ Advanced Controls</div>',
            unsafe_allow_html=True)

with st.expander("🔍 Filter Data",expanded=False):
    nc=st.multiselect("Category",_all_cats,default=st.session_state["f_cats"],key="f_cats_w")
    ns=st.multiselect("Status",_sta_all,default=st.session_state["f_sta"],key="f_sta_w")
    def _sl(lbl,lo,hi,dflt,k):
        if lo==hi: lo-=0.1; hi+=0.1
        return st.slider(lbl,lo,hi,dflt,key=k)
    nspi=_sl("SPI Range",_spi_mn,_spi_mx,st.session_state["f_spi"],"f_spi_w")
    ncpi=_sl("CPI Range",_cpi_mn,_cpi_mx,st.session_state["f_cpi"],"f_cpi_w")
    if st.button("Apply Filters"):
        st.session_state["f_cats"]=nc; st.session_state["f_sta"]=ns
        st.session_state["f_spi"]=nspi; st.session_state["f_cpi"]=ncpi; st.rerun()

with st.expander("📐 Quantity Mapping",expanded=False):
    mr=supabase.table("quantity_mapping").select("category","quantity_type").execute()
    md=pd.DataFrame(mr.data)
    if md.empty:
        defs=[{"category":c,"quantity_type":t} for c,t in [
            ("Walls","Area"),("Columns","Volume"),("Structural Framing","Length"),
            ("Roofs","Area"),("Floors","Area"),("Doors","Count"),("Windows","Count")]]
        for d in defs: supabase.table("quantity_mapping").upsert(d,on_conflict="category").execute()
        md=pd.DataFrame(defs)
    em=st.data_editor(md,use_container_width=True,key="qty_map_editor",
        column_config={"quantity_type":st.column_config.SelectboxColumn(
            "Quantity Type",options=["Volume","Area","Length","Count"],required=True)})
    if st.button("Save Quantity Mapping"):
        for _,row in em.iterrows():
            supabase.table("quantity_mapping").upsert(
                {"category":row["category"],"quantity_type":row["quantity_type"]},
                on_conflict="category").execute()
        st.success("Mapping saved!")

with st.expander("💰 Cost Recalculation",expanded=False):
    if st.button("🔄 Recalculate Costs"):
        c=recalc_costs(); st.success(f"Recalculated {c} elements (batched).")

with st.expander("📸 Photo Progress Sync",expanded=False):
    if st.button("📸 Update Progress from Photos"):
        u=update_progress_from_photos()
        if u: st.success(f"Updated {u} tasks."); st.rerun()
        else: st.info("No photos with Task ID found.")

with st.expander("✏️ Edit Elements",expanded=False):
    edf=elements_df[["task_id","unit_cost"]].copy()
    eel=st.data_editor(edf,use_container_width=True,key="elem_editor")
    if st.button("Save Element Changes"):
        for _,row in eel.iterrows():
            supabase.table("elements").update({"unit_cost":row["unit_cost"]})\
                    .eq("task_id",row["task_id"]).eq("project_id",project_id).execute()
        st.success("Saved!"); st.rerun()

# ════════════════════════════════════════════════════════════
#  FOOTER
# ════════════════════════════════════════════════════════════
st.markdown(f"""
<div style="text-align:center;padding:2.5rem 0 1rem;color:#1a2535;
  font-size:.6rem;letter-spacing:2.5px;text-transform:uppercase;">
  5D BIM Dashboard · {selected_project} · {today_str}
</div>""",unsafe_allow_html=True)
