# ============================================================
#  5D BIM Construction Dashboard  –  Complete Fixed Version
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
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER

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

# ============================  CSS (dark theme) ============================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&display=swap');
*{box-sizing:border-box;margin:0;padding:0;}
html,body,.stApp{background:#090b0f !important;font-family:'DM Sans',sans-serif;color:#dce8ff;}
header[data-testid="stHeader"]{display:none!important;}
#MainMenu,footer,.stDeployButton{display:none!important;}
.block-container{padding:1rem 1.4rem 2rem !important;max-width:100%!important;}
.card{background:#111622;border:1px solid rgba(255,255,255,0.06);border-radius:22px;padding:1.15rem 1.2rem;height:100%;}
.card-gradient{background:linear-gradient(145deg,#2a1765 0%,#6b1878 48%,#c42760 100%);border-radius:22px;padding:1.15rem 1.2rem;height:100%;}
.card-dark{background:#0d101a;border:1px solid rgba(255,255,255,0.05);border-radius:22px;padding:1.15rem 1.2rem;height:100%;}
.label{color:#5a6a8a;font-size:.84rem;text-transform:uppercase;letter-spacing:1.6px;font-weight:500;margin-bottom:1px;}
.big-val{color:#eef4ff;font-size:2.5rem;font-weight:700;font-family:'DM Sans',monospace;line-height:1.05;}
.med-val{color:#eef4ff;font-size:1.5rem;font-weight:600;line-height:1.1;}
.sm-val{color:#eef4ff;font-size:1.1rem;font-weight:600;}
.sub{color:rgba(255,255,255,.4);font-size:.72rem;margin-left:3px;}
.section-header{color:#eef4ff;font-size:.9rem;font-weight:700;text-transform:uppercase;letter-spacing:2px;margin-bottom:.9rem;opacity:.7;}
.brand{position:absolute;bottom:.9rem;right:1.1rem;font-size:.58rem;color:rgba(255,255,255,.18);text-transform:uppercase;}
.badge{display:inline-block;padding:2px 9px;border-radius:20px;font-size:.75rem;font-weight:700;text-transform:uppercase;}
.bg{background:rgba(0,255,136,.13);color:#00ff88;border:1px solid rgba(0,255,136,.3);}
.br{background:rgba(255,70,70,.13);color:#ff6b6b;border:1px solid rgba(255,70,70,.3);}
.ba{background:rgba(255,183,0,.13);color:#ffb700;border:1px solid rgba(255,183,0,.3);}
.bb{background:rgba(0,160,255,.13);color:#00aaff;border:1px solid rgba(0,160,255,.3);}
.kpi-row{display:flex;align-items:center;gap:.5rem;padding:.4rem 0;border-bottom:1px solid rgba(255,255,255,.04);}
.kpi-icon{font-size:1.1rem;width:22px;}
.kpi-text{flex:1;}
.kpi-label{font-size:.78rem;color:#5a6a8a;text-transform:uppercase;}
.kpi-val{font-size:1.1rem;font-weight:600;color:#eef4ff;}
.pbar-wrap{background:rgba(255,255,255,.07);border-radius:999px;height:5px;margin-top:4px;overflow:hidden;}
.pbar-fill{height:100%;border-radius:999px;background:linear-gradient(90deg,#00ff88,#00e0cc);}
.div{height:1px;background:linear-gradient(90deg,transparent,rgba(255,255,255,.08),transparent);margin:.9rem 0;}
.stButton>button{background:linear-gradient(135deg,#131d33,#0d1422);border:1px solid rgba(0,160,255,.25);border-radius:40px;color:#6ab4ff;font-size:.78rem;font-weight:500;width:100%;padding:.45rem 1rem;}
.stButton>button:hover{border-color:#00aaff;box-shadow:0 0 14px rgba(0,160,255,.3);color:#aad6ff;}
div[data-testid="stExpander"]{background:#0d101a;border:1px solid rgba(255,255,255,.06);border-radius:16px;}
div[data-testid="stMetric"]{display:none!important;}
.dash-header{display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:1.2rem;}
.dash-title{font-size:1.6rem;font-weight:700;color:#eef4ff;}
.dash-sub{font-size:.7rem;color:#3a4a62;margin-top:3px;}
.dash-time{font-size:.68rem;color:#3a4a62;text-align:right;}
</style>
""", unsafe_allow_html=True)

# ============================  PLOTLY THEME ============================
def dark_fig(fig):
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="DM Sans", color="#5a6a8a", size=11),
        margin=dict(l=10, r=10, t=30, b=10),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#6a8ab0", size=10)),
    )
    fig.update_xaxes(gridcolor="rgba(255,255,255,0.05)", showgrid=False, linecolor="rgba(255,255,255,0.05)")
    fig.update_yaxes(gridcolor="rgba(255,255,255,0.05)", showgrid=True, linecolor="rgba(0,0,0,0)")
    return fig

# ============================  SUPABASE ============================
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
merged["SPI"] = merged["earned_value"] / merged["planned_value"].replace(0, np.nan)
merged["CPI"] = merged["earned_value"] / merged["actual_cost"].replace(0, np.nan)
merged["SPI"] = merged["SPI"].clip(upper=3.0)
merged["CPI"] = merged["CPI"].clip(upper=3.0)
merged["Delayed"]    = merged["SPI"] < 1.0
merged["OverBudget"] = merged["CPI"] < 1.0

# ============================  SIDEBAR CONTROLS ============================
st.sidebar.markdown("## ⚙️ Controls")
extra_cost = st.sidebar.number_input("Extra Cost (KES)", value=0, step=1000)

proj_res = supabase.table("projects").select("extra_cost").eq("id", project_id).execute()
current_extra = proj_res.data[0]["extra_cost"] if proj_res.data else 0
if extra_cost != current_extra:
    supabase.table("projects").update({"extra_cost": extra_cost}).eq("id", project_id).execute()
    st.sidebar.success("Extra cost updated")

# ============================  FILTER STATE ============================
_all_cats   = list(merged["category"].unique())
_status_all = ["On Track", "Delayed", "Over Budget", "Delayed & Over"]
_spi_min    = float(merged["SPI"].min())
_spi_max    = float(merged["SPI"].max())
_cpi_min    = float(merged["CPI"].min())
_cpi_max    = float(merged["CPI"].max())
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

# ---- Helper functions ----
def recalc_costs():
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

# ============================  COMPUTE KPIs ============================
total_pv = filtered["planned_value"].sum()
total_ev = filtered["earned_value"].sum()
total_ac = filtered["actual_cost"].sum()
total_cost_all = filtered["total_cost"].sum()  # Total cost from Revit
overall_spi      = total_ev / total_pv if total_pv else 1.0
overall_cpi      = total_ev / total_ac if total_ac else 1.0
overall_progress_raw = (filtered["percent_complete"] * filtered["planned_value"]).sum() / total_pv if total_pv else 0
overall_progress = min(overall_progress_raw, 1.0)  # CAP at 100%
total_length = filtered["length"].sum() if "length" in filtered.columns else 0
num_elements = len(filtered)
num_categories = filtered["category"].nunique()
delayed_count = filtered["Delayed"].sum()
overbudget_count = filtered["OverBudget"].sum()
on_track = int(((~filtered["Delayed"]) & (~filtered["OverBudget"])).sum())

EAC = total_pv / overall_cpi if overall_cpi and overall_cpi != 0 else total_pv
ETC = EAC - total_ac
TCPI = (total_pv - total_ev) / (total_pv - total_ac) if (total_pv - total_ac) != 0 else 1.0

variance_cost = total_ev - total_ac
variance_sched = total_ev - total_pv

today_str = datetime.now().strftime("%b %d, %Y")
clock_str = datetime.now().strftime("%H:%M")

# Cost by category
cost_by_category = filtered.groupby("category")["total_cost"].sum().reset_index()
cost_by_category = cost_by_category.sort_values("total_cost", ascending=False)

# ============================  DASHBOARD HEADER ============================
st.markdown(f"""
<div class="dash-header">
  <div>
    <div class="dash-title">🏗️ {selected_project}</div>
    <div class="dash-sub">5D BIM · Construction Performance Dashboard</div>
  </div>
  <div class="dash-time">{clock_str}<br>{today_str}</div>
</div>
""", unsafe_allow_html=True)
st.caption("📌 SPI < 1 = behind schedule | CPI < 1 = over budget | Progress capped at 100%")

# ============================  ROW 1 — OVERVIEW CARDS ============================
c1, c2, c3 = st.columns([1, 1, 1], gap="small")

with c1:
    prog_pct = overall_progress * 100
    st.markdown(f"""
    <div class="card">
      <div class="section-header">Overall Progress</div>
      <div style="display:flex;justify-content:space-between;align-items:flex-start">
        <div><div class="big-val">{prog_pct:.1f}<span class="sub">%</span></div></div>
        <div style="text-align:right">
          <div class="label">On Track</div>
          <div class="med-val">{on_track}<span class="sub">/{num_elements}</span></div>
        </div>
      </div>
      <div class="pbar-wrap" style="margin-top:8px"><div class="pbar-fill" style="width:{prog_pct:.1f}%"></div></div>
      <div class="brand">BIM</div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="card">
      <div class="section-header">Financial Summary</div>
      <div class="kpi-row"><div class="kpi-icon">📐</div><div class="kpi-text"><div class="kpi-label">Earned Value</div><div class="kpi-val">{total_ev/1e6:.2f}M</div></div><div class="kpi-badge">{badge(overall_spi)}</div></div>
      <div class="kpi-row"><div class="kpi-icon">🔥</div><div class="kpi-text"><div class="kpi-label">Actual Cost</div><div class="kpi-val">{total_ac/1e6:.2f}M</div></div><div class="kpi-badge">{badge_cpi(overall_cpi)}</div></div>
      <div class="brand">BIM</div>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown(f"""
    <div class="card-dark">
      <div class="section-header">Forecast</div>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:.6rem">
        <div><div class="label">EAC</div><div class="sm-val" style="font-size:1rem">{EAC/1e6:.2f}M</div></div>
        <div><div class="label">ETC</div><div class="sm-val" style="font-size:1rem">{ETC/1e6:.2f}M</div></div>
        <div><div class="label">TCPI</div><div class="sm-val" style="font-size:1rem">{TCPI:.3f}</div></div>
        <div><div class="label">SPI</div><div class="sm-val" style="font-size:1rem">{overall_spi:.3f}</div></div>
      </div>
      <div class="brand">BIM</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

# ============================  COST BREAKDOWN SECTION ============================
st.subheader("💰 Total Cost Breakdown")

col_cost1, col_cost2 = st.columns([1, 1], gap="small")

with col_cost1:
    st.markdown(f"""
    <div class="card">
      <div class="section-header">Total Project Cost</div>
      <div class="big-val" style="font-size:2rem">{total_cost_all/1e6:.2f}<span class="sub">M KES</span></div>
      <div class="div"></div>
      <div class="label">Budget vs Actual</div>
      <div style="display:flex;justify-content:space-between;margin-top:5px">
        <span class="sm-val" style="font-size:0.9rem">Budget: {total_pv/1e6:.2f}M</span>
        <span class="sm-val" style="font-size:0.9rem">Actual: {total_ac/1e6:.2f}M</span>
      </div>
      <div class="brand">BIM</div>
    </div>
    """, unsafe_allow_html=True)

with col_cost2:
    fig_cost_bar = px.bar(
        cost_by_category.head(8),
        x="category",
        y="total_cost",
        title="Cost by Category (Top 8)",
        color="total_cost",
        color_continuous_scale="blues",
        text_auto='.2s'
    )
    fig_cost_bar.update_traces(textposition='outside')
    st.plotly_chart(dark_fig(fig_cost_bar), use_container_width=True, config={"displayModeBar": False})

st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

# ============================  ROW 2 — DONUT + EV BY CATEGORY ============================
col_left, col_right = st.columns([3, 2], gap="small")

with col_left:
    fig_donut = go.Figure(go.Pie(
        labels=cost_by_category["category"],
        values=cost_by_category["total_cost"],
        hole=0.5,
        marker=dict(colors=["#00aaff","#ff3d9a","#00ff88","#ffb700","#a855f7","#ff8c42","#00e0cc"]),
        textinfo="percent",
        textfont=dict(size=10, color="#eef4ff"),
        hovertemplate="<b>%{label}</b><br>%{value:,.0f} KES<extra></extra>",
    ))
    fig_donut.update_layout(title="Cost Breakdown by Category", height=320, margin=dict(l=0, r=0, t=40, b=0))
    st.plotly_chart(dark_fig(fig_donut), use_container_width=True, config={"displayModeBar": False})

with col_right:
    cat_ev = filtered.groupby("category")["earned_value"].sum().reset_index()
    fig_bar_ev = px.bar(cat_ev, x="category", y="earned_value", title="Earned Value by Category", color="earned_value", color_continuous_scale="teal")
    st.plotly_chart(dark_fig(fig_bar_ev), use_container_width=True, config={"displayModeBar": False})

st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

# ============================  GANTT CHART ============================
st.subheader("📅 Project Schedule (Gantt)")
if "start_date" in schedule_df.columns and "finish_date" in schedule_df.columns:
    sched_gantt = schedule_df.copy()
    sched_gantt["start_date"] = pd.to_datetime(sched_gantt["start_date"], errors='coerce')
    sched_gantt["finish_date"] = pd.to_datetime(sched_gantt["finish_date"], errors='coerce')
    sched_gantt = sched_gantt.dropna(subset=["start_date", "finish_date"])
    if not sched_gantt.empty:
        gantt_data = []
        for _, row in sched_gantt.iterrows():
            gantt_data.append(dict(
                Task=row["task_id"],
                Start=row["start_date"],
                Finish=row["finish_date"],
                Resource="Task",
                Complete=min(row.get("percent_complete", 0) / 100, 1.0)
            ))
        fig_gantt = ff.create_gantt(gantt_data, group_tasks=True, title="", height=400, show_colorbar=True)
        fig_gantt.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_gantt, use_container_width=True, config={"displayModeBar": False})
    else:
        st.info("No valid date ranges for Gantt chart. Ensure schedule_tasks has start_date and finish_date.")
else:
    st.info("Schedule missing start_date or finish_date columns. Gantt chart not available.")

st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

# ============================  RISK HEATMAP ============================
st.subheader("⚠️ Risk Heatmap")
heat_df = filtered[["task_id", "category", "SPI", "CPI", "Delayed", "OverBudget"]].copy()
heat_df["SPI"] = heat_df["SPI"].map("{:.3f}".format)
heat_df["CPI"] = heat_df["CPI"].map("{:.3f}".format)
def color_risk(val):
    try:
        v = float(val)
        if v < 0.8: return "background-color:#3d0f0f;color:#ff6b6b"
        if v < 0.95: return "background-color:#3d2e0f;color:#ffb700"
        return "background-color:#0f2e1a;color:#00ff88"
    except:
        return ""
styled_heat = heat_df.style.map(color_risk, subset=["SPI", "CPI"])
st.dataframe(styled_heat, use_container_width=True, height=300)

st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

# ============================  PHOTO UPLOAD (IN STREAMLIT) ============================
st.subheader("📸 Site Photos")

# Photo upload directly in Streamlit
uploaded_file = st.file_uploader("Upload a site photo", type=["jpg", "jpeg", "png"], key="photo_uploader_streamlit")
if uploaded_file is not None:
    try:
        # Upload to Supabase Storage
        file_bytes = uploaded_file.getvalue()
        file_name = f"photo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        supabase.storage.from_("photos").upload(file_name, file_bytes)
        public_url = supabase.storage.from_("photos").get_public_url(file_name)
        
        # Save to photos table
        supabase.table("photos").insert({
            "project_id": project_id,
            "task_id": None,
            "file_path": public_url,
            "caption": "Uploaded from dashboard",
            "uploaded_by": "Dashboard User",
            "completion_status": "Not Started"
        }).execute()
        st.success("Photo uploaded successfully!")
        st.rerun()
    except Exception as e:
        st.error(f"Upload failed: {e}")

# Display existing photos
if not photos_df.empty:
    cols = st.columns(3)
    for idx, (_, row) in enumerate(photos_df.head(6).iterrows()):
        with cols[idx % 3]:
            st.image(row["file_path"], caption=row.get("caption", ""), use_container_width=True)
            if row.get("task_id"):
                st.caption(f"Task: {row['task_id']} | Status: {row.get('completion_status', 'Not Started')}")
else:
    st.info("No photos uploaded yet. Use the uploader above to add site photos.")

st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

# ============================  COMMENTS ============================
st.subheader("💬 Comments")
for _, row in comments_df.head(10).iterrows():
    escaped_user = html.escape(str(row.get("user_name", "")))
    escaped_comment = html.escape(str(row.get("comment", "")))
    if row.get("is_emergency"):
        st.markdown(f"🚨 **{escaped_user}** (Emergency): {escaped_comment}")
    else:
        st.markdown(f"**{escaped_user}**: {escaped_comment}")

with st.form("comment_form", clear_on_submit=True):
    user = st.text_input("Your name", "Anonymous")
    comment = st.text_area("Comment", height=70)
    is_emg = st.checkbox("🚨 Mark as Emergency")
    if st.form_submit_button("Post Comment"):
        if not comment.strip():
            st.warning("Comment cannot be empty.")
        else:
            supabase.table("comments").insert({
                "project_id": project_id,
                "user_name": user,
                "comment": comment,
                "is_emergency": int(is_emg),
            }).execute()
            st.rerun()

st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

# ============================  PDF EXPORT ============================
st.subheader("📄 Export Report")
if st.button("Generate PDF Report"):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Centered', parent=styles['Normal'], alignment=TA_CENTER))
    
    story = [
        Paragraph(f"{selected_project} – 5D BIM Report", styles["Title"]),
        Spacer(1, 12),
        Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", styles["Normal"]),
        Spacer(1, 8),
        Paragraph(f"SPI: {overall_spi:.3f}  |  CPI: {overall_cpi:.3f}  |  Progress: {min(overall_progress*100, 100):.1f}%", styles["Normal"]),
        Spacer(1, 6),
        Paragraph(f"Planned Value: {total_pv:,.0f} KES", styles["Normal"]),
        Paragraph(f"Earned Value:  {total_ev:,.0f} KES", styles["Normal"]),
        Paragraph(f"Actual Cost:   {total_ac:,.0f} KES", styles["Normal"]),
        Paragraph(f"Total Cost (BIM): {total_cost_all:,.0f} KES", styles["Normal"]),
        Spacer(1, 6),
        Paragraph(f"Delayed Tasks: {int(delayed_count)}  |  Over Budget: {int(overbudget_count)}  |  On Track: {on_track}", styles["Normal"]),
        Spacer(1, 12),
        Paragraph("Cost Breakdown by Category", styles["Heading2"]),
    ]
    
    cat_data = [["Category", "Total Cost (KES)"]]
    for _, row in cost_by_category.iterrows():
        cat_data.append([row["category"], f"{row['total_cost']:,.0f}"])
    table = Table(cat_data, repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#2a1765")),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("FONTSIZE", (0,0), (-1,-1), 9),
        ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#f5f5f5")]),
    ]))
    story.append(table)
    doc.build(story)
    st.download_button(
        "⬇️ Download PDF Report",
        buffer.getvalue(),
        file_name=f"bim_report_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
        mime="application/pdf",
    )

st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

# ============================  CONTROLS & FILTERS (bottom) ============================
st.markdown('<div class="section-header" style="opacity:.4">⚙️ Advanced Controls</div>', unsafe_allow_html=True)

with st.expander("🔍 Filter Data", expanded=False):
    new_cats = st.multiselect("Category", options=_all_cats, default=st.session_state["f_cats"], key="f_cats_widget")
    new_status = st.multiselect("Status", _status_all, default=st.session_state["f_status"], key="f_status_widget")
    new_spi = st.slider("SPI Range", _spi_min, _spi_max, st.session_state["f_spi"], key="f_spi_widget")
    new_cpi = st.slider("CPI Range", _cpi_min, _cpi_max, st.session_state["f_cpi"], key="f_cpi_widget")
    if st.button("Apply Filters"):
        st.session_state["f_cats"] = new_cats
        st.session_state["f_status"] = new_status
        st.session_state["f_spi"] = new_spi
        st.session_state["f_cpi"] = new_cpi
        st.rerun()

with st.expander("📐 Quantity Mapping", expanded=False):
    map_response = supabase.table("quantity_mapping").select("category", "quantity_type").execute()
    map_df = pd.DataFrame(map_response.data)
    if map_df.empty:
        default_mapping = [
            {"category": "Walls", "quantity_type": "Area"},
            {"category": "Columns", "quantity_type": "Volume"},
            {"category": "Structural Framing", "quantity_type": "Length"},
            {"category": "Roofs", "quantity_type": "Area"},
            {"category": "Floors", "quantity_type": "Area"},
            {"category": "Doors", "quantity_type": "Count"},
            {"category": "Windows", "quantity_type": "Count"},
        ]
        for item in default_mapping:
            supabase.table("quantity_mapping").upsert(item, on_conflict="category").execute()
        map_df = pd.DataFrame(default_mapping)
    edited_map = st.data_editor(map_df, use_container_width=True, key="qty_map_editor")
    if st.button("Save Quantity Mapping"):
        for _, row in edited_map.iterrows():
            supabase.table("quantity_mapping").upsert({"category": row["category"], "quantity_type": row["quantity_type"]}, on_conflict="category").execute()
        st.success("Mapping saved!")

with st.expander("💰 Cost Recalculation", expanded=False):
    if st.button("🔄 Recalculate Costs"):
        c = recalc_costs()
        st.success(f"Recalculated {c} elements.")

with st.expander("📸 Photo Progress Sync", expanded=False):
    if st.button("📸 Update Progress from Photos"):
        updated = update_progress_from_photos()
        if updated:
            st.success(f"Updated {updated} tasks.")
            st.rerun()
        else:
            st.info("No photos with Task ID found.")

with st.expander("✏️ Edit Elements (Unit Cost / Task ID)", expanded=False):
    edit_df = elements_df[["task_id", "unit_cost"]].copy()
    edited_elems = st.data_editor(edit_df, use_container_width=True, key="elem_editor")
    if st.button("Save Element Changes"):
        for _, row in edited_elems.iterrows():
            supabase.table("elements").update({"unit_cost": row["unit_cost"]}).eq("task_id", row["task_id"]).eq("project_id", project_id).execute()
        st.success("Saved!"); st.rerun()

# ============================  FOOTER ============================
st.markdown(f"""
<div style="text-align:center;padding:2rem 0 1rem;color:#1e2d42;font-size:.65rem;text-transform:uppercase">
  5D BIM Dashboard · {selected_project} · {today_str}
</div>
""", unsafe_allow_html=True)

# Helper functions for badges (must be defined before use)
def badge(val, lo=0.95, hi=1.0):
    if val >= hi: return '<span class="badge bg">On Track</span>'
    if val >= lo: return '<span class="badge ba">Warning</span>'
    return '<span class="badge br">Behind</span>'

def badge_cpi(val):
    if val >= 1.0: return '<span class="badge bg">Under Budget</span>'
    if val >= 0.9: return '<span class="badge ba">Warning</span>'
    return '<span class="badge br">Over Budget</span>'
