import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np

# ==========================================
# 1. PAGE CONFIGURATION & STYLING
# ==========================================
st.set_page_config(page_title="V.F.R Digital Parameter Matrix", page_icon="⚙️", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    .stSelectbox label, .stRadio label, .stSlider label, .stTextInput label { font-weight: bold; }
    hr { margin: 15px 0 !important; opacity: 0.3; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. MULTI-LANGUAGE DICTIONARY (EN/VN)
# ==========================================
if "lang" not in st.session_state:
    st.session_state.lang = "EN"

def toggle_lang():
    st.session_state.lang = "VN" if st.session_state.lang == "EN" else "EN"

T = {
    "EN": {
        "title": "V.F.R Digital Parameter Matrix",
        "btn_lang": "🇻🇳 Chuyển sang Tiếng Việt",
        "sec_param": "PARAMETER SELECTION",
        "sec_dash": "LIVE OPTIMAL DASHBOARD",
        "scan_title": "(0) Process Scanning",
        "scan_ph": "Scan Barcode or Enter Process ID",
        "btn_load": "Load Preset",
        "msg_load": "ALORA 45 loaded!",
        "msg_err": "Code not found!",
        "sub_title": "(1) Substrate Specifications",
        "sub_type": "Substrate Type",
        "sub_mat": "Specific Material",
        "sub_thick": "Core Thickness",
        "ven_title": "(2) Veneer Specifications",
        "ven_sides": "Veneer Sides",
        "v1": "1 Side", "v2": "2 Sides",
        "ven_mat": "Veneer Material",
        "ven_thick": "Veneer Thickness",
        "glue_title": "(3) Glue Specifications",
        "glue_type": "Glue Type",
        "glue_spread": "Glue Spread (gr/m²)",
        "btn_opt": "Optimize Parameters",
        "msg_opt": "Parameters successfully optimized for Job:",
        "temp_title": "MACHINE TEMPERATURE",
        "temp_sub": "Selected: Press 03, Heater 1 & 2",
        "temp_tgt": "Target: ± 3°C Tolerance | <span style='color:#00E676'>**OPTIMAL**</span>",
        "time_title": "PRESSING TIME",
        "time_sub": "Line A, Station 1",
        "time_rem": "Remaining",
        "time_cyc": "Cycle Count",
        "press": "Pressure",
        "speed": "Feed Speed",
        "stab": "Process Stability",
        "mon_title": "OPERATIONS MONITOR",
        "mon_tgt": "Target",
        "mon_comp": "Completed",
        "mon_units": "units"
    },
    "VN": {
        "title": "Ma Trận Thông Số Kỹ Thuật Số V.F.R",
        "btn_lang": "🇬🇧 Switch to English",
        "sec_param": "CHỌN THÔNG SỐ ĐẦU VÀO",
        "sec_dash": "BẢNG ĐIỀU KHIỂN TỐI ƯU (TRỰC TIẾP)",
        "scan_title": "(0) Quét Mã Quy Trình",
        "scan_ph": "Quét mã vạch hoặc nhập mã ID",
        "btn_load": "Tải Dữ Liệu",
        "msg_load": "Đã tải thông số cửa ALORA 45!",
        "msg_err": "Không tìm thấy mã!",
        "sub_title": "(1) Thông Số Phôi (Lõi)",
        "sub_type": "Loại Phôi",
        "sub_mat": "Vật Liệu Cụ Thể",
        "sub_thick": "Độ Dày Phôi",
        "ven_title": "(2) Thông Số Veneer (Ván lạng)",
        "ven_sides": "Số Mặt Veneer",
        "v1": "1 Mặt", "v2": "2 Mặt",
        "ven_mat": "Loại Gỗ Veneer",
        "ven_thick": "Độ Dày Veneer",
        "glue_title": "(3) Thông Số Keo",
        "glue_type": "Loại Keo",
        "glue_spread": "Lượng Keo Phủ (gr/m²)",
        "btn_opt": "Tối Ưu Hóa Thông Số",
        "msg_opt": "Đã tối ưu thành công thông số cho Lệnh:",
        "temp_title": "NHIỆT ĐỘ MÁY ÉP",
        "temp_sub": "Máy chọn: Ép 03, Bộ gia nhiệt 1 & 2",
        "temp_tgt": "Mục tiêu: Dung sai ± 3°C | <span style='color:#00E676'>**TỐI ƯU**</span>",
        "time_title": "THỜI GIAN ÉP",
        "time_sub": "Chuyền A, Trạm 1",
        "time_rem": "Còn lại",
        "time_cyc": "Chu kỳ",
        "press": "Áp Suất Máy",
        "speed": "Tốc Độ Nạp",
        "stab": "Độ Ổn Định",
        "mon_title": "GIÁM SÁT SẢN XUẤT",
        "mon_tgt": "Mục tiêu",
        "mon_comp": "Đã xong",
        "mon_units": "sản phẩm"
    }
}
L = T[st.session_state.lang] # Lấy bộ từ điển hiện tại

# ==========================================
# HEADER & LANGUAGE TOGGLE
# ==========================================
h1, h2, h3 = st.columns([0.6, 3.5, 1.5])
with h1:
    try: st.image("logo.png", width=90)
    except: st.write("⚙️")
with h2:
    st.title(L["title"])
with h3:
    st.markdown("<br>", unsafe_allow_html=True)
    st.button(L["btn_lang"], on_click=toggle_lang, use_container_width=True)

st.markdown("---")

# ==========================================
# SESSION STATE & DOE LOGIC
# ==========================================
SUBSTRATE_DATA = {
    "WOOD": ["ACACIA", "ASH", "BEECH", "OAK", "POPLAR", "TEAK", "EUCALYPTUS"],
    "BOARD": ["PLYWOOD - SHANGWOOD", "PLYWOOD - POPLAR", "LVL PLYWOOD - SHANGWOOD", "MDF - DONGWHA"]
}

if "sub_type_key" not in st.session_state:
    st.session_state.update({
        "sub_type_key": "BOARD", "sub_desc_key": "PLYWOOD - SHANGWOOD", "thickness_key": "18mm",
        "veneer_sides_key": "1 Side", "veneer_mat_key": "Walnut", "veneer_thick_key": "0.6mm",
        "glue_type_key": "UF", "glue_spread_key": 120
    })

def get_optimized_parameters(sub_type, sub_desc, thickness, veneer_sides, veneer_thickness, glue_type, glue_spread):
    base_temp, base_time, base_press = 180, 200, 90
    if sub_type == "BOARD" and "MDF" in sub_desc: base_temp += 5; base_press += 5
    elif sub_type == "WOOD": base_temp += 8; base_time += 15
    base_time += (int(thickness.replace("mm","")) - 15) * 5
    if veneer_sides == "2 Sides": base_time += 25 
    if veneer_thickness in ["0.9mm", "5mm"]: base_time += 15; base_temp += 2
    if glue_type == "UF": base_temp += 8 
    elif glue_type in ["EPI", "AB"]: base_temp -= 5 
    if glue_spread > 120: base_time += (glue_spread - 120) * 0.5 
    return {"temp": round(base_temp, 1), "time": int(base_time), "press": round(base_press, 1)}

# ==========================================
# LAYOUT DESIGN
# ==========================================
col1, col2 = st.columns([1.3, 2.7])

with col1:
    st.subheader(L["sec_param"])
    
    # 0. Barcode Scanner
    st.markdown(f"**{L['scan_title']}**")
    bc1, bc2 = st.columns([3, 1.5])
    with bc1: barcode = st.text_input("Barcode", placeholder=L["scan_ph"], label_visibility="collapsed")
    with bc2:
        if st.button(L["btn_load"], use_container_width=True):
            if barcode.strip() == "2COM1HP-001":
                st.session_state.update({
                    "sub_type_key": "BOARD", "sub_desc_key": "PLYWOOD - POPLAR", "thickness_key": "15mm",
                    "veneer_sides_key": "2 Sides", "veneer_mat_key": "Oak", "veneer_thick_key": "5mm",
                    "glue_type_key": "AB", "glue_spread_key": 125
                })
                st.success(L["msg_load"])
            else:
                st.error(L["msg_err"])
    st.markdown("<hr>", unsafe_allow_html=True)
    
    # 1. Substrate
    st.markdown(f"**{L['sub_title']}**")
    c1, c2 = st.columns(2)
    with c1: sub_type = st.selectbox(L["sub_type"], list(SUBSTRATE_DATA.keys()), key="sub_type_key")
    with c2:
        if st.session_state.sub_desc_key not in SUBSTRATE_DATA[sub_type]: st.session_state.sub_desc_key = SUBSTRATE_DATA[sub_type][0]
        sub_desc = st.selectbox(L["sub_mat"], SUBSTRATE_DATA[sub_type], key="sub_desc_key")
    thickness = st.selectbox(L["sub_thick"], ["12mm", "15mm", "18mm", "20mm"], key="thickness_key")
    st.markdown("<hr>", unsafe_allow_html=True)
    
    # 2. Veneer
    st.markdown(f"**{L['ven_title']}**")
    
    # Render VN/EN choices properly while keeping underlying code logic in English
    v_sides_display = [L["v1"], L["v2"]]
    v_sides_internal = ["1 Side", "2 Sides"]
    curr_v_idx = v_sides_internal.index(st.session_state.veneer_sides_key)
    
    sel_v_side_display = st.radio(L["ven_sides"], v_sides_display, index=curr_v_idx, horizontal=True)
    st.session_state.veneer_sides_key = v_sides_internal[v_sides_display.index(sel_v_side_display)]
    veneer_sides = st.session_state.veneer_sides_key

    c3, c4 = st.columns(2)
    with c3: veneer_material = st.selectbox(L["ven_mat"], ["Oak", "Walnut", "Beech", "Poplar", "Maple"], key="veneer_mat_key")
    with c4: veneer_thickness = st.selectbox(L["ven_thick"], ["0.3mm", "0.6mm", "0.9mm", "5mm"], key="veneer_thick_key")
    st.markdown("<hr>", unsafe_allow_html=True)
    
    # 3. Glue
    st.markdown(f"**{L['glue_title']}**")
    glue_type = st.selectbox(L["glue_type"], ["PVAc", "UF", "AB", "EPI"], key="glue_type_key")
    glue_spread = st.slider(L["glue_spread"], min_value=80, max_value=200, step=5, key="glue_spread_key")
    
    st.markdown("<br>", unsafe_allow_html=True)
    optimize_clicked = st.button(L["btn_opt"], type="primary", use_container_width=True)

with col2:
    st.subheader(L["sec_dash"])
    
    if optimize_clicked:
        optimized_data = get_optimized_parameters(sub_type, sub_desc, thickness, veneer_sides, veneer_thickness, glue_type, glue_spread)
        st.success(f"{L['msg_opt']} {barcode if barcode else sub_desc}!")
    else:
        optimized_data = {"temp": 185.7, "time": 240, "press": 95.0}

    dash_col1, dash_col2 = st.columns(2)
    
    with dash_col1:
        st.markdown(f"### {L['temp_title']}")
        st.markdown(L["temp_sub"])
        st.markdown(f"<h1 style='color: #00E676; font-size: 4rem; margin: 0;'>{optimized_data['temp']} °C</h1>", unsafe_allow_html=True)
        
        np.random.seed(42) 
        temp_data = pd.DataFrame({"Time": range(1, 21), "Temp": np.random.normal(optimized_data['temp'], 1.2, 20)})
        fig_temp = go.Figure(go.Scatter(x=temp_data['Time'], y=temp_data['Temp'], mode='lines', line=dict(color='#00BFFF', width=3)))
        fig_temp.update_layout(height=180, margin=dict(l=0, r=0, t=10, b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis=dict(showgrid=False, visible=False), yaxis=dict(showgrid=False, range=[optimized_data['temp']-5, optimized_data['temp']+5]))
        st.plotly_chart(fig_temp, use_container_width=True)
        st.markdown(L["temp_tgt"], unsafe_allow_html=True)

with dash_col2:
        st.markdown(f"### {L['time_title']}")
        st.markdown(L["time_sub"])
        
        # 1. Chuyển đổi tổng giây sang định dạng Phút:Giây (MM:SS)
        total_seconds = optimized_data['time']
        mins, secs = divmod(total_seconds, 60)
        time_str = f"{mins:02d}:{secs:02d}"
        
        # 2. Vẽ biểu đồ Gauge (tắt con số mặc định bằng cách chỉ dùng mode="gauge")
        fig_gauge = go.Figure(go.Indicator(
            mode = "gauge", 
            value = total_seconds,
            gauge = {
                'axis': {'range': [None, 350], 'tickwidth': 1, 'tickcolor': "white"}, 
                'bar': {'color': "#00BFFF"},
                'bgcolor': "rgba(0,0,0,0)", 'borderwidth': 2, 'bordercolor': "gray",
                'steps': [
                    {'range': [0, 200], 'color': "rgba(255, 255, 255, 0.1)"}, 
                    {'range': [200, 350], 'color': "rgba(255, 255, 255, 0.2)"}
                ]
            }
        ))
        
        # 3. Chèn text MM:SS vào chính giữa tâm biểu đồ
        fig_gauge.add_annotation(
            x=0.5, y=0.35, # Căn chỉnh tọa độ x,y để chữ nằm ngay giữa lõi
            text=time_str,
            font=dict(size=55, color="white"),
            showarrow=False
        )
        
        fig_gauge.update_layout(height=230, margin=dict(l=20, r=20, t=20, b=20), paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_gauge, use_container_width=True)
        st.markdown(f"{L['time_rem']}: **03:59** | {L['time_cyc']}: 1 | <span style='color:#00E676'>**ACTIVE**</span>", unsafe_allow_html=True)

    st.markdown("---")
    
    kpi_col1, kpi_col2, kpi_col3 = st.columns(3)
    kpi_col1.metric(label=L["press"], value=f"{optimized_data['press']} MPa")
    kpi_col2.metric(label=L["speed"], value="12.5 m/min")
    kpi_col3.metric(label=L["stab"], value="98.3%")
    
    st.markdown("---")
    st.markdown(f"**{L['mon_title']}**")
    st.progress(115/250, text=f"Job ID: {barcode if barcode else 'PWOOD18W'} | {L['mon_tgt']}: 250 {L['mon_units']} | {L['mon_comp']}: 115")
