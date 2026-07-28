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
