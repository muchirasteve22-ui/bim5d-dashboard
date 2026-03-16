import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from services.supabase_client import get_supabase

st.set_page_config(page_title="Project Dashboard", page_icon="📊", layout="wide")

# Custom CSS for better appearance (optional)
st.markdown("""
<style>
    .kpi-card { background-color: #1e2128; border-radius: 10px; padding: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }
</style>
""", unsafe_allow_html=True)

supabase = get_supabase()

# ---- Load projects ----
projects = supabase.table('projects').select('*').execute()
projects_df = pd.DataFrame(projects.data)
if projects_df.empty:
    st.warning("No projects found. Please add a project in Supabase first.")
    st.stop()

project_names = projects_df['name'].tolist()
selected_project = st.sidebar.selectbox("🏢 Select Project", project_names)
project_id = projects_df[projects_df['name'] == selected_project]['id'].iloc[0]

# ---- Load data for selected project ----
@st.cache_data(ttl=60)
def load_elements(pid):
    response = supabase.table('elements').select('*').eq('project_id', pid).execute()
    return pd.DataFrame(response.data)

@st.cache_data(ttl=60)
def load_schedule(pid):
    response = supabase.table('schedule_tasks').select('*').eq('project_id', pid).execute()
    return pd.DataFrame(response.data)

@st.cache_data(ttl=60)
def load_comments(pid):
    response = supabase.table('comments').select('*').eq('project_id', pid).order('created_at', desc=True).execute()
    return pd.DataFrame(response.data)

elements_df = load_elements(project_id)
schedule_df = load_schedule(project_id)
comments_df = load_comments(project_id)

if elements_df.empty or schedule_df.empty:
    st.warning("No data for this project yet. Please run the sync tool to upload data.")
    st.stop()

# ---- Merge elements with schedule on task_id ----
merged = pd.merge(elements_df, schedule_df, on='task_id', how='inner')

# Calculate SPI and CPI
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

filtered = merged[merged['category'].isin(categories)]

# ---- KPI Cards ----
total_pv = filtered['planned_value'].sum()
total_ev = filtered['earned_value'].sum()
total_ac = filtered['actual_cost'].sum()
overall_spi = total_ev / total_pv if total_pv else 1
overall_cpi = total_ev / total_ac if total_ac else 1

st.title(f"🏗️ {selected_project} – 5D BIM Dashboard")
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.metric("Planned (PV)", f"{total_pv:,.0f} KES")
with col2:
    st.metric("Earned (EV)", f"{total_ev:,.0f} KES", delta=f"{total_ev/total_pv-1:+.1%}")
with col3:
    st.metric("Actual (AC)", f"{total_ac:,.0f} KES", delta=f"{total_ac/total_pv-1:+.1%}")
with col4:
    st.metric("SPI", f"{overall_spi:.3f}", delta="Behind" if overall_spi<1 else "Ahead", delta_color="inverse")
with col5:
    st.metric("CPI", f"{overall_cpi:.3f}", delta="Over" if overall_cpi<1 else "Under", delta_color="inverse")

# ---- Cost Breakdown Pie Chart ----
st.subheader("💰 Cost Breakdown by Category")
cost_by_cat = filtered.groupby('category')['total_cost'].sum().reset_index()
fig_pie = px.pie(cost_by_cat, values='total_cost', names='category', title="Total Cost by Category", hole=0.4)
st.plotly_chart(fig_pie, use_container_width=True)

# ---- Planned vs Actual Bar Chart ----
st.subheader("📊 Planned vs Actual Cost by Category")
cat_summary = filtered.groupby('category').agg({'planned_value':'sum', 'actual_cost':'sum'}).reset_index()
fig_bar = px.bar(cat_summary, x='category', y=['planned_value','actual_cost'], 
                 title="Planned vs Actual", barmode='group',
                 labels={'value':'Cost (KES)', 'variable':''})
st.plotly_chart(fig_bar, use_container_width=True)

# ---- Risk Heatmap ----
st.subheader("⚠️ Risk Heatmap")
heat_cols = ['task_id', 'category', 'planned_value', 'actual_cost', 'SPI', 'CPI', 'Delayed', 'OverBudget']
heat_df = filtered[heat_cols].copy()
# Format numbers
heat_df['planned_value'] = heat_df['planned_value'].map('{:,.0f}'.format)
heat_df['actual_cost'] = heat_df['actual_cost'].map('{:,.0f}'.format)
heat_df['SPI'] = heat_df['SPI'].map('{:.3f}'.format)
heat_df['CPI'] = heat_df['CPI'].map('{:.3f}'.format)

def color_risk(val):
    if isinstance(val, str):
        try:
            val = float(val)
        except:
            return ''
    if val < 0.8:
        return 'background-color: #8B0000; color: white'
    elif val < 0.95:
        return 'background-color: #FF8C00; color: white'
    else:
        return 'background-color: #2E7D32; color: white'

styled = heat_df.style.applymap(color_risk, subset=['SPI','CPI'])
st.dataframe(styled, use_container_width=True, height=400)

# ---- Monte Carlo Simulation ----
st.subheader("🎲 Monte Carlo Forecast")
num_sim = st.slider("Number of simulations", 100, 2000, 500)
spi_vals = filtered['SPI'].dropna()
if len(spi_vals) > 0:
    # Simulate project durations assuming planned duration of 100 days (you can adjust)
    planned_duration = 100
    sim_spi = np.random.choice(spi_vals, size=(num_sim, len(spi_vals)), replace=True)
    sim_duration = planned_duration / sim_spi.mean(axis=1)
    fig_hist = px.histogram(sim_duration, nbins=50, title="Simulated Project Durations",
                            labels={'value':'Duration (days)'})
    fig_hist.add_vline(x=planned_duration, line_dash="dash", line_color="green", annotation_text="Planned")
    p80 = np.percentile(sim_duration, 80)
    fig_hist.add_vline(x=p80, line_dash="dash", line_color="red", annotation_text="P80")
    st.plotly_chart(fig_hist, use_container_width=True)
    col1, col2 = st.columns(2)
    with col1:
        st.metric("P50 Duration", f"{np.median(sim_duration):.0f} days")
    with col2:
        st.metric("P80 Duration", f"{p80:.0f} days")
else:
    st.info("Not enough SPI data for simulation.")

# ---- Comments Section ----
st.subheader("💬 Project Comments")

# Display existing comments
for _, row in comments_df.iterrows():
    st.markdown(f"**{row['user_name']}** ({row['created_at'][:10]}):")
    st.markdown(row['comment'])
    st.markdown("---")

# Form to add a new comment
with st.form("comment_form"):
    user_name = st.text_input("Your name", value="Anonymous")
    new_comment = st.text_area("Leave a comment or instruction")
    submitted = st.form_submit_button("Post Comment")
    if submitted and new_comment:
        supabase.table('comments').insert({
            "project_id": project_id,
            "user_name": user_name,
            "comment": new_comment
        }).execute()
        st.success("Comment posted!")
        st.rerun()