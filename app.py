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
    .stSelectbox label, .stRadio label, .stSlider label { color: #FAFAFA !important; font-weight: bold; }
    hr { margin: 15px 0 !important; opacity: 0.3; }
    </style>
""", unsafe_allow_html=True)

st.title("⚙️ V.F.R Digital Parameter Matrix")
st.markdown("---")

# ==========================================
# 2. DATA DICTIONARY (From User's Excel)
# ==========================================
SUBSTRATE_DATA = {
    "WOOD": ["ACACIA", "ASH", "BEECH", "OAK", "POPLAR", "TEAK", "EUCALYPTUS"],
    "BOARD": ["PLYWOOD - SHANGWOOD", "LVL PLYWOOD - SHANGWOOD", "MDF - DONGWHA"]
}

# ==========================================
# 3. SIMULATED DOE MODEL LOGIC
# ==========================================
def get_optimized_parameters(sub_type, sub_desc, thickness, veneer_sides, veneer_material, veneer_thickness, glue_type, glue_spread):
    """
    Simulates a DOE model response based on selections.
    """
    base_temp, base_time, base_press = 180, 200, 90
    
    # 1. Substrate & Thickness Adjustments
    if sub_type == "BOARD" and "MDF" in sub_desc:
        base_temp += 5
        base_press += 5
    elif sub_type == "WOOD":
        base_temp += 8  # Solid wood requires slightly higher temp
        base_time += 15
    
    thick_val = int(thickness.replace("mm",""))
    base_time += (thick_val - 15) * 5

    # 2. Veneer Config
    if veneer_sides == "2 Sides":
        base_time += 25 
    
    if veneer_thickness == "0.6mm":
        base_time += 5
    elif veneer_thickness == "0.9mm":
        base_time += 10
        base_temp += 2

    # 3. Glue Specs
    if glue_type == "UF":
        base_temp += 8 
    elif glue_type == "EPI":
        base_temp -= 5 
        
    if glue_spread > 120:
        base_time += (glue_spread - 120) * 0.5 

    return {
        "temp": round(base_temp, 1),
        "time": int(base_time),
        "press": round(base_press, 1)
    }

# ==========================================
# 4. LAYOUT DESIGN: Input & Output
# ==========================================
col1, col2 = st.columns([1.3, 2.7])

# COLUMN 1: PARAMETER SELECTION
with col1:
    st.subheader("PARAMETER SELECTION")
    
    # --- Substrate Specs ---
    st.markdown("**(1) Substrate Specifications**")
    c1, c2 = st.columns(2)
    with c1:
        # First Dropdown (Type)
        sub_type = st.selectbox("Substrate Type", list(SUBSTRATE_DATA.keys()), index=1)
    with c2:
        # Second Dropdown (Description) - Dependent on First Dropdown
        sub_desc = st.selectbox("Specific Material", SUBSTRATE_DATA[sub_type])
        
    thickness = st.selectbox("Core Thickness", ["12mm", "15mm", "18mm", "20mm"], index=2)
    
    # --- Veneer Specs ---
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("**(2) Veneer Specifications**")
    veneer_sides = st.radio("Veneer Sides", ["1 Side", "2 Sides"], horizontal=True)
    
    c3, c4 = st.columns(2)
    with c3:
        veneer_material = st.selectbox("Veneer Material", ["Oak", "Walnut", "Beech", "Poplar", "Maple"], index=1)
    with c4:
        veneer_thickness = st.selectbox("Veneer Thickness", ["0.3mm", "0.6mm", "0.9mm"])

    # --- Glue Specs ---
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("**(3) Glue Specifications**")
    glue_type = st.selectbox("Glue Type", ["PVAc", "UF", "AB", "EPI"], index=1)
    glue_spread = st.slider("Glue Spread (gr/m²)", min_value=80, max_value=200, value=120, step=5)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Optimize Button
    optimize_clicked = st.button("Optimize Parameters", type="primary", use_container_width=True)

# COLUMN 2: LIVE OPTIMAL DASHBOARD
with col2:
    st.subheader("LIVE OPTIMAL DASHBOARD")
    
    # Perform simulation based on new inputs
    if optimize_clicked:
        optimized_data = get_optimized_parameters(sub_type, sub_desc, thickness, veneer_sides, veneer_material, veneer_thickness, glue_type, glue_spread)
        st.success(f"Parameters successfully optimized for {sub_desc}!")
    else:
        optimized_data = {"temp": 185.7, "time": 240, "press": 95.0}

    # Top Row: Machine Temp & Pressing Time
    dash_col1, dash_col2 = st.columns(2)
    
    with dash_col1:
        st.markdown("### MACHINE TEMPERATURE")
        st.markdown("Selected: Press 03, Heater 1 & 2")
        st.markdown(f"<h1 style='color: #00E676; font-size: 4rem; margin: 0;'>{optimized_data['temp']} °C</h1>", unsafe_allow_html=True)
        
        np.random.seed(42) 
        temp_data = pd.DataFrame({
            "Time": range(1, 21),
            "Temp": np.random.normal(optimized_data['temp'], 1.2, 20)
        })
        fig_temp = go.Figure(go.Scatter(x=temp_data['Time'], y=temp_data['Temp'], mode='lines', line=dict(color='#00BFFF', width=3)))
        fig_temp.update_layout(height=180, margin=dict(l=0, r=0, t=10, b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis=dict(showgrid=False, visible=False), yaxis=dict(showgrid=False, range=[optimized_data['temp']-5, optimized_data['temp']+5]))
        st.plotly_chart(fig_temp, use_container_width=True)
        st.markdown("**Target: ± 3°C Tolerance** | <span style='color:#00E676'>**OPTIMAL**</span>", unsafe_allow_html=True)

    with dash_col2:
        st.markdown("### PRESSING TIME")
        st.markdown("Line A, Station 1")
        
        fig_gauge = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = optimized_data['time'],
            number = {'suffix': " Sec", 'font': {'color': 'white'}},
            gauge = {
                'axis': {'range': [None, 350], 'tickwidth': 1, 'tickcolor': "white"},
                'bar': {'color': "#00BFFF"},
                'bgcolor': "rgba(0,0,0,0)",
                'borderwidth': 2,
                'bordercolor': "gray",
                'steps': [
                    {'range': [0, 200], 'color': "rgba(255, 255, 255, 0.1)"},
                    {'range': [200, 350], 'color': "rgba(255, 255, 255, 0.2)"}],
            }
        ))
        fig_gauge.update_layout(height=230, margin=dict(l=20, r=20, t=20, b=20), paper_bgcolor='rgba(0,0,0,0)', font={'color': "white"})
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
    st.progress(115/250, text=f"Job ID: PWOOD18W | Target: 250 units | Completed: 115")
