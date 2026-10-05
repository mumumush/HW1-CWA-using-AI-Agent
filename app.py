"""
Taiwan Weather Forecast Web App
Built with Streamlit, Python, CWA Open Data API, SQLite, and Folium.
Created using Antigravity AI Agent & Gemini.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from streamlit_folium import st_folium
import os
from datetime import datetime

from src.cwa_api import fetch_cwa_weather, COUNTY_REGIONS
from src.database import (
    init_db, save_forecast_records, get_latest_forecasts, 
    get_regional_summary, DEFAULT_DB_PATH
)
from src.map_utils import create_taiwan_weather_map, get_weather_icon, REGION_COLORS

# Page Configuration
st.set_page_config(
    page_title="Taiwan Weather Forecast | 台灣天氣預報",
    page_icon="🌤️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern glassmorphism & cards styling
st.markdown("""
<style>
    /* Metric Card Styling */
    .metric-card {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.9), rgba(243, 244, 246, 0.9));
        border-radius: 12px;
        padding: 16px 20px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
        border: 1px solid rgba(229, 231, 235, 0.8);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.08);
    }
    .region-badge {
        display: inline-block;
        padding: 2px 10px;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 12px;
        color: white;
    }
    .weather-card {
        border-radius: 12px;
        padding: 14px 16px;
        margin-bottom: 12px;
        background: white;
        border: 1px solid #E2E8F0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        transition: all 0.2s;
    }
    .weather-card:hover {
        border-color: #3B82F6;
        box-shadow: 0 4px 14px rgba(59, 130, 246, 0.15);
    }
</style>
""", unsafe_allow_html=True)


# Initialize Database
init_db()

# --- Sidebar Controls ---
with st.sidebar:
    st.image("https://img.icons8.com/clouds/200/sun.png", width=90)
    st.title("氣象設定與控制台")
    st.caption("Powered by CWA API × SQLite × AI Agent")
    
    st.markdown("---")
    
    # API Key Input
    api_key = st.text_input(
        "🔑 CWA API 授權碼 (可選)",
        value="",
        type="password",
        placeholder="例如：CWA-XXXXXXXX-XXXX...",
        help="如無授權碼將自動使用內建完整台灣示範氣象數據，隨開即用！"
    )
    st.caption("👉 免費申請授權碼：[氣象署開放資料平臺](https://opendata.cwa.gov.tw/)")
    
    # Refresh button
    col_btn1, col_btn2 = st.columns([1, 1])
    with col_btn1:
        refresh_clicked = st.button("🔄 更新資料", use_container_width=True)
    with col_btn2:
        use_demo = st.button("🧪 示範數據", use_container_width=True)
        
    st.markdown("---")
    
    # Region filter
    selected_region = st.selectbox(
        "📍 選擇地區篩選",
        options=["全部地區", "北部", "中部", "南部", "東部", "外島"],
        index=0
    )
    
    # Period Selector
    period_option = st.radio(
        "⏱️ 預報時間區間",
        options=[
            ("0", "未來 12 小時 (今明首段)"),
            ("1", "12 ~ 24 小時 (今明次段)"),
            ("2", "24 ~ 36 小時 (後續時段)")
        ],
        format_func=lambda x: x[1]
    )
    selected_period = int(period_option[0])
    
    st.markdown("---")
    st.markdown("""
    **專案特色亮點**：
    - ⚡ **即時 CWA API 串接**
    - 💾 **SQLite 資料庫持久化**
    - 🗺️ **Folium 台灣互動地圖**
    - 📊 **Plotly 氣溫與降雨分析**
    - 🤖 **Antigravity AI Agent 構建**
    """)


# --- Data Fetching & Sync Logic ---
# Cache session state for forecasts
if "last_fetch_time" not in st.session_state or refresh_clicked or use_demo:
    current_key = "" if use_demo else api_key
    with st.spinner("正在獲取中央氣象署最新天氣資料..."):
        records, msg, is_live = fetch_cwa_weather(current_key)
        saved_count = save_forecast_records(records)
        st.session_state["records"] = records
        st.session_state["status_msg"] = msg
        st.session_state["is_live"] = is_live
        st.session_state["last_fetch_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Retrieve filtered data from SQLite
current_forecasts = get_latest_forecasts(selected_period)
regional_summaries = get_regional_summary(selected_period)

# Apply Region Filter
if selected_region != "全部地區":
    filtered_forecasts = [f for f in current_forecasts if f["region"] == selected_region]
else:
    filtered_forecasts = current_forecasts


# --- Header Section ---
header_col1, header_col2 = st.columns([3, 1])
with header_col1:
    st.title("🌤️ 台灣各縣市天氣預報儀表板")
    st.markdown("**Taiwan Weather Forecast Dashboard** — 由 Antigravity × Gemini × GitHub 協同打造")
with header_col2:
    status_color = "green" if st.session_state.get("is_live", False) else "orange"
    st.markdown(f"""
    <div style="text-align: right; margin-top: 10px;">
        <span style="background-color: {status_color}; color: white; padding: 4px 10px; border-radius: 8px; font-size: 13px; font-weight: 600;">
            {'🟢 連線氣象署即時 API' if st.session_state.get('is_live', False) else '🟡 示範與資料庫快取模式'}
        </span>
        <div style="font-size: 12px; color: #64748B; margin-top: 5px;">
            更新時間: {st.session_state.get('last_fetch_time', '-')}
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")


# --- Top Regional Summary Cards (Matching Workshop Diagram Step 9!) ---
st.subheader("📊 各大生活圈氣溫概況")
summary_cols = st.columns(len(regional_summaries) if regional_summaries else 5)

for idx, r in enumerate(regional_summaries):
    reg_name = r["region"]
    min_t = r["min_temp"]
    max_t = r["max_temp"]
    avg_pop = int(r["avg_pop"])
    color = REGION_COLORS.get(reg_name, "#3B82F6")
    
    with summary_cols[idx]:
        st.markdown(f"""
        <div class="metric-card" style="border-top: 4px solid {color};">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span class="region-badge" style="background: {color};">{reg_name}</span>
                <span style="font-size: 12px; color: #6B7280;">降雨 {avg_pop}%</span>
            </div>
            <div style="font-size: 26px; font-weight: 800; color: #1F2937; margin: 8px 0 4px 0;">
                {min_t}° ~ {max_t}°<span style="font-size: 14px; font-weight: 500; color: #6B7280;">C</span>
            </div>
            <div style="font-size: 12px; color: #4B5563;">
                涵蓋 {r['county_count']} 個縣市
            </div>
        </div>
        """, unsafe_allow_html=True)

st.write("")


# --- Main Content: Map & Forecast Table (Step 9 Layout) ---
st.markdown("### 🗺️ 台灣互動天氣地圖與詳細數據")

tab_map, tab_cards, tab_charts, tab_db = st.tabs([
    "📍 互動地圖與總覽", 
    "🗂️ 縣市天氣卡片", 
    "📈 氣溫與降雨圖表", 
    "💾 SQLite 資料庫紀錄"
])

with tab_map:
    map_col, table_col = st.columns([1.3, 1])
    
    with map_col:
        st.markdown("##### 📍 台灣全區氣溫分佈地圖 (點擊標記查看詳情)")
        weather_map = create_taiwan_weather_map(filtered_forecasts)
        st_folium(weather_map, width="100%", height=480)
        
    with table_col:
        st.markdown("##### 📋 預報清單")
        if filtered_forecasts:
            df_display = pd.DataFrame(filtered_forecasts)[[
                "region", "location_name", "wx", "min_t", "max_t", "pop", "ci"
            ]]
            df_display.columns = ["分區", "縣市", "天氣狀況", "最低溫(°C)", "最高溫(°C)", "降雨機率(%)", "舒適度"]
            st.dataframe(
                df_display,
                use_container_width=True,
                height=480,
                hide_index=True
            )
        else:
            st.info("該分區目前無符合的資料。")

with tab_cards:
    st.markdown("##### 🏙️ 各縣市詳細預報卡片")
    card_cols = st.columns(3)
    
    for i, item in enumerate(filtered_forecasts):
        col = card_cols[i % 3]
        wx_icon = get_weather_icon(item["wx"])
        region = item["region"]
        badge_color = REGION_COLORS.get(region, "#3B82F6")
        
        with col:
            st.markdown(f"""
            <div class="weather-card">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <h3 style="margin: 0; font-size: 18px; color: #1E293B;">{item['location_name']}</h3>
                    <span class="region-badge" style="background: {badge_color};">{region}</span>
                </div>
                <div style="font-size: 28px; margin: 8px 0; display: flex; align-items: center; gap: 8px;">
                    <span>{wx_icon}</span>
                    <span style="font-size: 16px; font-weight: 600; color: #334155;">{item['wx']}</span>
                </div>
                <div style="display: flex; justify-content: space-between; margin-bottom: 6px;">
                    <span style="color: #64748B; font-size: 13px;">🌡️ 溫度範圍</span>
                    <strong style="color: #0F172A; font-size: 14px;">{item['min_t']}°C ~ {item['max_t']}°C</strong>
                </div>
                <div style="display: flex; justify-content: space-between; margin-bottom: 6px;">
                    <span style="color: #64748B; font-size: 13px;">💧 降雨機率</span>
                    <strong style="color: #0284C7; font-size: 14px;">{item['pop']}%</strong>
                </div>
                <div style="font-size: 12px; color: #64748B; border-top: 1px dashed #E2E8F0; padding-top: 6px; margin-top: 6px;">
                    🛋️ {item['ci']}
                </div>
            </div>
            """, unsafe_allow_html=True)

with tab_charts:
    st.markdown("##### 📊 氣溫分佈與降雨機率分析")
    if filtered_forecasts:
        df_chart = pd.DataFrame(filtered_forecasts)
        
        col_c1, col_c2 = st.columns(2)
        
        with col_c1:
            fig_temp = go.Figure()
            fig_temp.add_trace(go.Bar(
                x=df_chart["location_name"],
                y=df_chart["max_t"] - df_chart["min_t"],
                base=df_chart["min_t"],
                marker_color='#3B82F6',
                name="氣溫區間 (°C)",
                hovertemplate='%{x}: %{base}°C ~ %{customdata}°C<extra></extra>',
                customdata=df_chart["max_t"]
            ))
            fig_temp.update_layout(
                title="各縣市氣溫範圍 (最低溫 ~ 最高溫)",
                xaxis_title="縣市",
                yaxis_title="氣溫 (°C)",
                template="plotly_white",
                height=400
            )
            st.plotly_chart(fig_temp, use_container_width=True)
            
        with col_c2:
            fig_pop = px.bar(
                df_chart.sort_values(by="pop", ascending=False),
                x="location_name",
                y="pop",
                color="pop",
                color_continuous_scale="Blues",
                title="各縣市降雨機率排行 (%)",
                labels={"pop": "降雨機率 (%)", "location_name": "縣市"},
                template="plotly_white",
                height=400
            )
            st.plotly_chart(fig_pop, use_container_width=True)

with tab_db:
    st.markdown("##### 💾 SQLite 資料庫存儲狀況")
    st.write(f"資料庫檔案路徑: `{DEFAULT_DB_PATH}`")
    
    if filtered_forecasts:
        df_all = pd.DataFrame(filtered_forecasts)
        st.write(f"目前載入預報筆數: **{len(df_all)}** 筆")
        st.dataframe(df_all, use_container_width=True)
        
        csv_data = df_all.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="📥 匯出當前天氣資料 (CSV)",
            data=csv_data,
            file_name=f"taiwan_weather_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #94A3B8; font-size: 13px; padding-bottom: 20px;">
    🚀 Antigravity x Gemini x GitHub | HW1 CWA Weather Forecast Web App | 煥哥 Vibe Coding 實作專案
</div>
""", unsafe_allow_html=True)
