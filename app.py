%%writefile app.py
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np

# ==========================================
# 1. PAGE & SIMULATION CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="V.F.R Digital Parameter Matrix",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS to mimic dark mode and styling
st.markdown("""
    <style>
    .main { background-color: #0E1117; }
    h1, h2, h3, p, label { color: #FAFAFA !important; }
    div[data-testid="stMetricValue"] > div { color: #FAFAFA !important; }
    .stSelectbox label { color: #FAFAFA !important; }
    </style>
""", unsafe_allow_html=True)

st.title("⚙️ V.F.R Digital Parameter Matrix")
st.markdown("---")

# ==========================================
# 2. SIMULATED DOE MODEL LOGIC
# ==========================================
def get_optimized_parameters(substrate, thickness, veneer):
    """
    Simulates a DOE model response based on selections.
    Replace with your actual regression formula.
    """
    base_temp, base_time, base_press = 180, 200, 90

    # Define factor adjustments
    if substrate == "MDF":
        base_temp += 10 # MDF needs higher temp
        base_time += 30
        base_press += 10

    # Thickness factor
    thick_val = int(thickness.replace("mm",""))
    if thick_val > 15:
        base_temp += (thick_val - 15) * 1 # minor temp increase
        base_time += (thick_val - 15) * 5 # significant time increase

    # Veneer factor (relative to Oak)
    if veneer == "Walnut Veneer":
        base_temp -= 2
        base_time += 10
    elif veneer == "Maple":
        base_temp += 3
        base_time -= 5

    # Return simulated optimal values
    return {
        "temp": round(base_temp, 1),
        "time": int(base_time),
        "press": round(base_press, 1)
    }

# ==========================================
# 3. LAYOUT DESIGN: Input & Output
# ==========================================
col1, col2 = st.columns([1, 2.5])

# COLUMN 1: PARAMETER SELECTION
with col1:
    st.subheader("PARAMETER SELECTION")

    # The dropdowns (selectbox) Di requested
    substrate = st.selectbox("Substrate Material", ["Plywood", "MDF"])
    thickness = st.selectbox("Core Thickness", ["15mm", "18mm", "20mm"], index=1)
    veneer = st.selectbox("Veneer Type", ["Oak", "Walnut Veneer", "Maple"], index=1)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"**CURRENT SELECTION:**<br>{substrate} / {thickness} / {veneer}", unsafe_allow_html=True)
    st.markdown("**Configuration Status:** ✅ Ready")

    # Demo simulation button
    optimize_clicked = st.button("Optimize Parameters", type="primary", use_container_width=True)

# COLUMN 2: LIVE OPTIMAL DASHBOARD
with col2:
    st.subheader("LIVE OPTIMAL DASHBOARD")

    # Perform optimization (or simulation)
    if optimize_clicked:
        optimized_data = get_optimized_parameters(substrate, thickness, veneer)
        st.success(f"Parameters optimized based on simulated DOE Digital Matrix!")
    else:
        # Placeholder values before click
        optimized_data = {"temp": 185.7, "time": 240, "press": 95.0}

    # Top Row: Machine Temp & Pressing Time
    dash_col1, dash_col2 = st.columns(2)

    with dash_col1:
        st.markdown("### MACHINE TEMPERATURE")
        st.markdown("Selected: Press 03, Heater 1 & 2")
        st.markdown(f"<h1 style='color: #00E676;'>{optimized_data['temp']} °C</h1>", unsafe_allow_html=True)

        # Simulate Temperature Fluctuation Line Chart
        np.random.seed(42) # repeatable demo data
        temp_data = pd.DataFrame({
            "Time": range(1, 21),
            "Temp": np.random.normal(optimized_data['temp'], 1.5, 20)
        })
        fig_temp = go.Figure(go.Scatter(x=temp_data['Time'], y=temp_data['Temp'], mode='lines', line=dict(color='#00BFFF', width=3)))
        fig_temp.update_layout(height=200, margin=dict(l=0, r=0, t=0, b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis=dict(showgrid=False, visible=False), yaxis=dict(showgrid=False))
        st.plotly_chart(fig_temp, use_container_width=True)
        st.markdown("**Target: 180-190°C** | <span style='color:#00E676'>**OPTIMAL**</span>", unsafe_allow_html=True)

    with dash_col2:
        st.markdown("### PRESSING TIME")
        st.markdown("Line A, Station 1")

        # Gauge Chart for Time
        fig_gauge = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = optimized_data['time'],
            number = {'suffix': " Sec", 'font': {'color': 'white'}},
            gauge = {
                'axis': {'range': [None, 300], 'tickwidth': 1, 'tickcolor': "white"},
                'bar': {'color': "#00BFFF"},
                'bgcolor': "rgba(0,0,0,0)",
                'borderwidth': 2,
                'bordercolor': "gray",
                'steps': [
                    {'range': [0, 180], 'color': "rgba(255, 255, 255, 0.1)"},
                    {'range': [180, 300], 'color': "rgba(255, 255, 255, 0.2)"}],
            }
        ))
        fig_gauge.update_layout(height=250, margin=dict(l=20, r=20, t=30, b=20), paper_bgcolor='rgba(0,0,0,0)', font={'color': "white"})
        st.plotly_chart(fig_gauge, use_container_width=True)
        st.markdown("Remaining: **03:59** | Cycle Count: 1 | <span style='color:#00E676'>**ACTIVE**</span>", unsafe_allow_html=True)

    st.markdown("---")

    # Bottom Row: Secondary KPIs
    kpi_col1, kpi_col2, kpi_col3 = st.columns(3)
    kpi_col1.metric(label="Pressure", value=f"{optimized_data['press']} PSI")
    kpi_col2.metric(label="Feed Speed", value="12.5 m/min")
    kpi_col3.metric(label="Process Stability", value="98.3%")

    st.markdown("---")
    st.markdown("**OPERATIONS MONITOR**")
    st.progress(115/250, text="Job ID: PWOOD18W | Target: 250 units | Completed: 115")