# dashboard.py (corrected – use .map instead of .applymap)
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from supabase import create_client
import os
from datetime import datetime
import io
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

# ===== CONFIGURATION =====
SUPABASE_URL = st.secrets["supabase_url"] if "supabase_url" in st.secrets else os.environ.get("SUPABASE_URL")
SUPABASE_KEY = st.secrets["supabase_key"] if "supabase_key" in st.secrets else os.environ.get("SUPABASE_KEY")
PROJECT_NAME = "Kakamega Assembly Hall"
# =========================

st.set_page_config(page_title="5D BIM Dashboard", page_icon="🏗️", layout="wide")

# ---- Custom iQON-style theme ----
def apply_custom_theme():
    st.markdown("""
    <style>
    /* ===== GLOBAL BACKGROUND — deep near-black like iQON ===== */
    html, body, .stApp {
        background: #0d0d0f !important;
        color: #e8eaf0;
    }

    /* ===== MAIN CONTAINER — subtle border glow only, no fill glow ===== */
    .block-container {
        background: #111318;
        padding: 2rem;
        border-radius: 16px;
        border: 1px solid rgba(30, 120, 255, 0.55);
        box-shadow:
            0 0 0 1px rgba(30, 120, 255, 0.15),
            0 0 30px rgba(30, 120, 255, 0.25),
            0 0 80px rgba(30, 120, 255, 0.08);
    }

    /* ===== KPI METRIC BOXES — border glow only, dark fill ===== */
    div[data-testid="stMetric"] {
        background: #13161e;
        padding: 15px;
        border-radius: 12px;
        border: 1px solid rgba(40, 140, 255, 0.45);
        box-shadow:
            0 0 8px rgba(40, 140, 255, 0.35),
            0 0 20px rgba(40, 140, 255, 0.12);
        transition: box-shadow 0.3s ease, border-color 0.3s ease;
    }

    div[data-testid="stMetric"]:hover {
        border-color: rgba(80, 180, 255, 0.75);
        box-shadow:
            0 0 14px rgba(60, 160, 255, 0.6),
            0 0 35px rgba(30, 120, 255, 0.25);
    }

    div[data-testid="stMetric"] label,
    div[data-testid="stMetricLabel"] {
        color: #8899bb !important;
        font-size: 0.78rem;
        letter-spacing: 0.08em;
        text-transform: uppercase;
    }

    div[data-testid="stMetricValue"] {
        color: #ddeeff !important;
    }

    section[data-testid="stSidebar"] {
        background: #0f1117 !important;
        border-right: 1px solid rgba(30, 120, 255, 0.3);
        box-shadow: 2px 0 20px rgba(30, 120, 255, 0.08);
    }

    .stButton > button {
        background: #131a2e;
        color: #7ab8ff;
        border: 1px solid rgba(50, 140, 255, 0.5);
        border-radius: 8px;
        box-shadow: 0 0 8px rgba(40, 130, 255, 0.3);
        transition: 0.25s ease;
    }

    .stButton > button:hover {
        background: #1a2540;
        border-color: rgba(80, 180, 255, 0.8);
        box-shadow: 0 0 16px rgba(60, 160, 255, 0.5);
        color: #b8d9ff;
    }

    .stDataFrame {
        background: #13161e !important;
        border-radius: 10px;
        border: 1px solid rgba(40, 120, 255, 0.25);
    }

    h1, h2, h3 {
        color: #c5deff;
        text-shadow: none;
        letter-spacing: -0.01em;
    }

    .stSelectbox > div, .stMultiSelect > div, .stSlider > div {
        background: #13161e !important;
        border-color: rgba(40, 120, 255, 0.3) !important;
    }

    .stSlider [data-baseweb="slider"] [role="slider"] {
        background: #2e7fff !important;
        box-shadow: 0 0 8px rgba(46, 127, 255, 0.7);
    }

    .stForm {
        background: #13161e;
        border: 1px solid rgba(40, 120, 255, 0.25);
        border-radius: 12px;
        padding: 1rem;
    }

    .stAlert {
        border-radius: 10px;
        border-left: 3px solid #2e7fff;
    }
    </style>
    """, unsafe_allow_html=True)

apply_custom_theme()

# ---- Supabase connection ----
@st.cache_resource
def init_supabase():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = init_supabase()

# ---- Load projects ----
@st.cache_data(ttl=60)
def load_projects():
    res = supabase.table('projects').select('*').execute()
    return pd.DataFrame(res.data)

projects_df = load_projects()
if projects_df.empty:
    st.warning("No projects found. Please add a project in Supabase.")
    st.stop()

project_names = projects_df['name'].tolist()
selected_project = st.sidebar.selectbox("🏢 Select Project", project_names)
project_id = projects_df[projects_df['name'] == selected_project]['id'].iloc[0]

# ---- Load data ----
@st.cache_data(ttl=60)
def load_elements(pid):
    res = supabase.table('elements').select('*').eq('project_id', pid).execute()
    return pd.DataFrame(res.data)

@st.cache_data(ttl=60)
def load_schedule(pid):
    res = supabase.table('schedule_tasks').select('*').eq('project_id', pid).execute()
    return pd.DataFrame(res.data)

@st.cache_data(ttl=60)
def load_comments(pid):
    res = supabase.table('comments').select('*').eq('project_id', pid).order('created_at', desc=True).execute()
    return pd.DataFrame(res.data)

@st.cache_data(ttl=60)
def load_photos(pid):
    res = supabase.table('photos').select('*').eq('project_id', pid).order('uploaded_at', desc=True).execute()
    return pd.DataFrame(res.data)

@st.cache_data(ttl=60)
def load_spi_history(pid):
    res = supabase.table('spi_history').select('*').eq('project_id', pid).order('recorded_at', desc=True).execute()
    return pd.DataFrame(res.data)

elements_df = load_elements(project_id)
schedule_df = load_schedule(project_id)
comments_df = load_comments(project_id)
photos_df = load_photos(project_id)
spi_history_df = load_spi_history(project_id)

if elements_df.empty or schedule_df.empty:
    st.warning("No data for this project. Please run the sync tool to upload data.")
    st.stop()

# ---- Merge and EVM ----
merged = pd.merge(elements_df, schedule_df, on='task_id', how='inner')
merged['SPI'] = merged['earned_value'] / merged['planned_value']
merged['CPI'] = merged['earned_value'] / merged['actual_cost']
merged['Delayed'] = merged['SPI'] < 1.0
merged['OverBudget'] = merged['CPI'] < 1.0

# ---- Sidebar Filters ----
st.sidebar.header("🔍 Filters")
categories = st.sidebar.multiselect(
    "Category",
    options=merged['category'].unique(),
    default=merged['category'].unique()
)

status_options = ["On Track", "Delayed", "Over Budget", "Delayed & Over"]
status_filter = st.sidebar.multiselect("Status", status_options, default=status_options)
status_conditions = []
if "On Track" in status_filter:
    status_conditions.append((~merged['Delayed']) & (~merged['OverBudget']))
if "Delayed" in status_filter:
    status_conditions.append(merged['Delayed'] & (~merged['OverBudget']))
if "Over Budget" in status_filter:
    status_conditions.append((~merged['Delayed']) & merged['OverBudget'])
if "Delayed & Over" in status_filter:
    status_conditions.append(merged['Delayed'] & merged['OverBudget'])
final_status = status_conditions[0] if status_conditions else pd.Series([True]*len(merged))
for cond in status_conditions[1:]:
    final_status |= cond

spi_min, spi_max = st.sidebar.slider(
    "SPI Range", min_value=float(merged['SPI'].min()), max_value=float(merged['SPI'].max()),
    value=(float(merged['SPI'].min()), float(merged['SPI'].max()))
)
cpi_min, cpi_max = st.sidebar.slider(
    "CPI Range", min_value=float(merged['CPI'].min()), max_value=float(merged['CPI'].max()),
    value=(float(merged['CPI'].min()), float(merged['CPI'].max()))
)

filtered = merged[
    (merged['category'].isin(categories)) &
    (final_status) &
    (merged['SPI'].between(spi_min, spi_max)) &
    (merged['CPI'].between(cpi_min, cpi_max))
]

# ---- Extra Cost (Editable) ----
proj_res = supabase.table('projects').select('extra_cost').eq('id', project_id).execute()
extra_cost = proj_res.data[0]['extra_cost'] if proj_res.data else 0
new_extra = st.sidebar.number_input("Extra Cost (KES)", value=float(extra_cost), step=1000.0)
if new_extra != extra_cost:
    supabase.table('projects').update({'extra_cost': new_extra}).eq('id', project_id).execute()
    st.success("Extra cost updated!")

# ---- Quantity Mapping Editor ----
st.sidebar.subheader("📐 Quantity Mapping")
map_response = supabase.table('quantity_mapping').select('category', 'quantity_type').execute()
map_df = pd.DataFrame(map_response.data)
if map_df.empty:
    default_mapping = [
        {'category': 'Walls', 'quantity_type': 'Volume'},
        {'category': 'Columns', 'quantity_type': 'Volume'},
        {'category': 'Structural Framing', 'quantity_type': 'Length'},
        {'category': 'Roofs', 'quantity_type': 'Area'},
        {'category': 'Floors', 'quantity_type': 'Area'},
        {'category': 'Doors', 'quantity_type': 'Length'},
        {'category': 'Windows', 'quantity_type': 'Area'}
    ]
    map_df = pd.DataFrame(default_mapping)
edited_map = st.sidebar.data_editor(map_df, use_container_width=True, key="map_editor")
if st.sidebar.button("Save Mapping"):
    for _, row in edited_map.iterrows():
        supabase.table('quantity_mapping').upsert({
            "category": row['category'],
            "quantity_type": row['quantity_type']
        }).execute()
    st.success("Mapping updated! Next sync will use new settings.")
    st.rerun()

# ---- Top Metrics ----
total_pv = filtered['planned_value'].sum()
total_ev = filtered['earned_value'].sum()
total_ac = filtered['actual_cost'].sum()
overall_spi = total_ev / total_pv if total_pv else 1.0
overall_cpi = total_ev / total_ac if total_ac else 1.0
overall_progress = (filtered['percent_complete'] * filtered['planned_value']).sum() / total_pv if total_pv else 0

st.title(f"🏗️ {selected_project} – 5D BIM Dashboard")
st.markdown("---")

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Planned Value", f"{total_pv:,.0f} KES")
col2.metric("Earned Value", f"{total_ev:,.0f} KES", delta=f"{total_ev/total_pv-1:+.1%}")
col3.metric("Actual Cost", f"{total_ac:,.0f} KES", delta=f"{total_ac/total_pv-1:+.1%}")
col4.metric("SPI", f"{overall_spi:.3f}", delta="Behind" if overall_spi<1 else "Ahead", delta_color="inverse")
col5.metric("CPI", f"{overall_cpi:.3f}", delta="Over" if overall_cpi<1 else "Under", delta_color="inverse")

col6, col7, col8, col9 = st.columns(4)
col6.metric("Categories", filtered['category'].nunique())
col7.metric("Elements", len(filtered))
col8.metric("Progress", f"{overall_progress*100:.1f}%")
total_length = filtered['length'].sum() if 'length' in filtered.columns else 0
col9.metric("Total Length", f"{total_length:,.2f} m" if total_length else "N/A")
col10 = st.columns(1)[0]
col10.metric("Extra Cost", f"{new_extra:,.0f} KES")

# ---- Predictive Delay Warning ----
st.subheader("🔮 Predictive Delay Warning")
if not spi_history_df.empty:
    spi_history_df['recorded_at'] = pd.to_datetime(spi_history_df['recorded_at'])
    spi_trend = spi_history_df.sort_values(['task_id', 'recorded_at'], ascending=[True, False])
    spi_trend = spi_trend.groupby('task_id').head(3)
    decreasing_tasks = []
    for task_id, group in spi_trend.groupby('task_id'):
        if len(group) >= 3:
            spis = group.sort_values('recorded_at')['spi'].values
            if spis[0] > spis[1] > spis[2]:
                decreasing_tasks.append(task_id)
    if decreasing_tasks:
        st.warning(f"⚠️ Potential delay risk for tasks: {', '.join(decreasing_tasks)}. SPI has been decreasing for 3 consecutive updates.")
    else:
        st.success("No negative SPI trends detected.")
else:
    st.info("Not enough SPI history for trend analysis. Run sync tool at least 3 times.")

# ---- Charts ----
st.subheader("📊 Cost & Progress Overview")
col_left, col_right = st.columns(2)
with col_left:
    cost_by_cat = filtered.groupby('category')['total_cost'].sum().reset_index()
    fig_pie = px.pie(cost_by_cat, values='total_cost', names='category', title="Cost by Category", hole=0.4)
    st.plotly_chart(fig_pie, use_container_width=True)
with col_right:
    cat_summary = filtered.groupby('category').agg({'planned_value':'sum', 'actual_cost':'sum'}).reset_index()
    fig_bar = px.bar(cat_summary, x='category', y=['planned_value','actual_cost'], barmode='group', title="Planned vs Actual")
    st.plotly_chart(fig_bar, use_container_width=True)

# ---- Risk Heatmap ----
st.subheader("⚠️ Risk Heatmap")
heat_cols = ['task_id', 'category', 'planned_value', 'actual_cost', 'SPI', 'CPI', 'Delayed', 'OverBudget']
heat_df = filtered[heat_cols].copy()
heat_df['planned_value'] = heat_df['planned_value'].map('{:,.0f}'.format)
heat_df['actual_cost'] = heat_df['actual_cost'].map('{:,.0f}'.format)
heat_df['SPI'] = heat_df['SPI'].map('{:.3f}'.format)
heat_df['CPI'] = heat_df['CPI'].map('{:.3f}'.format)

def color_risk(val):
    if isinstance(val, str):
        try: val = float(val)
        except: return ''
    if val < 0.8: return 'background-color: #8B0000; color: white'
    elif val < 0.95: return 'background-color: #FF8C00; color: white'
    else: return 'background-color: #2E7D32; color: white'

styled = heat_df.style.map(color_risk, subset=['SPI','CPI'])   # <-- FIXED: changed applymap to map
st.dataframe(styled, use_container_width=True, height=400)

# ---- Monte Carlo ----
st.subheader("🎲 Monte Carlo Forecast")
num_sim = st.slider("Simulations", 100, 5000, 1000)
spi_vals = filtered['SPI'].dropna()
if len(spi_vals) > 0:
    planned_duration = 100
    sim_spi = np.random.choice(spi_vals, size=(num_sim, len(spi_vals)), replace=True)
    sim_duration = planned_duration / sim_spi.mean(axis=1)
    fig_hist = px.histogram(sim_duration, nbins=50, title="Simulated Project Durations")
    fig_hist.add_vline(x=planned_duration, line_dash="dash", line_color="green", annotation_text="Planned")
    p80 = np.percentile(sim_duration, 80)
    fig_hist.add_vline(x=p80, line_dash="dash", line_color="red", annotation_text="P80")
    st.plotly_chart(fig_hist, use_container_width=True)
    st.metric("P80 Duration", f"{p80:.0f} days")
else:
    st.info("Not enough SPI data for simulation.")

# ---- Photo‑to‑Schedule Matching ----
st.subheader("📸 Site Photos with Task Progress")
if not photos_df.empty:
    photos_with_progress = pd.merge(photos_df, schedule_df, left_on='task_id', right_on='task_id', how='left')
    for _, row in photos_with_progress.iterrows():
        with st.container():
            st.image(row['file_path'], caption=row['caption'], width=300)
            if pd.notna(row.get('task_id')):
                progress = row.get('percent_complete', 0)
                st.write(f"**Linked to task:** {row['task_id']} – Progress: {progress:.1f}%")
                st.progress(progress/100)
            else:
                st.write("Not linked to any task.")
else:
    st.info("No photos uploaded yet.")

# ---- Comments ----
st.subheader("💬 Comments")
for _, row in comments_df.iterrows():
    if row['is_emergency']:
        st.error(f"🚨 **{row['user_name']}** (Emergency): {row['comment']}")
    else:
        st.markdown(f"**{row['user_name']}**: {row['comment']}")
with st.form("comment_form"):
    user = st.text_input("Your name", "Anonymous")
    comment = st.text_area("Leave a comment")
    if st.form_submit_button("Post"):
        supabase.table('comments').insert({"project_id": project_id, "user_name": user, "comment": comment, "is_emergency": 0}).execute()
        st.success("Comment posted!"); st.rerun()

# ---- PDF Report ----
st.subheader("📄 PDF Report")
if st.button("Generate PDF"):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = [Paragraph(f"{selected_project} – 5D BIM Report", styles['Title']),
             Spacer(1,12),
             Paragraph(f"SPI: {overall_spi:.3f}, CPI: {overall_cpi:.3f}", styles['Normal']),
             Spacer(1,12),
             Paragraph(f"PV: {total_pv:,.0f} KES, EV: {total_ev:,.0f} KES, AC: {total_ac:,.0f} KES", styles['Normal'])]
    doc.build(story)
    st.download_button("Download Report", buffer.getvalue(), file_name="bim_report.pdf", mime="application/pdf")
