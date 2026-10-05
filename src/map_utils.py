"""
Map visualization utilities using Folium for Taiwan Weather Forecast.
"""
import folium
from folium.plugins import MiniMap
from typing import List, Dict, Any
from src.cwa_api import COUNTY_COORDINATES

REGION_COLORS = {
    "北部": "#3B82F6",   # Blue
    "中部": "#10B981",   # Green
    "南部": "#F59E0B",   # Amber / Orange
    "東部": "#8B5CF6",   # Purple
    "外島": "#EC4899",   # Pink
    "其他": "#6B7280"
}

def get_weather_icon(wx: str) -> str:
    """Return an emoji or icon representation for weather condition."""
    if "雨" in wx:
        return "🌧️"
    elif "陰" in wx:
        return "☁️"
    elif "多雲" in wx:
        return "⛅"
    elif "晴" in wx:
        return "☀️"
    elif "霧" in wx:
        return "🌫️"
    return "🌤️"


def create_taiwan_weather_map(forecast_records: List[Dict[str, Any]]) -> folium.Map:
    """
    Generate an interactive Taiwan map with county weather markers and tooltip popups.
    """
    # Center around Taiwan
    m = folium.Map(
        location=[23.75, 120.95],
        zoom_start=7,
        tiles="CartoDB positron",
        control_scale=True,
        prefer_canvas=True
    )

    for item in forecast_records:
        loc_name = item.get("location_name")
        if loc_name not in COUNTY_COORDINATES:
            continue
            
        lat, lon = COUNTY_COORDINATES[loc_name]
        region = item.get("region", "北部")
        color = REGION_COLORS.get(region, "#3B82F6")
        
        min_t = item.get("min_t", 20)
        max_t = item.get("max_t", 28)
        pop = item.get("pop", 0)
        wx = item.get("wx", "晴")
        ci = item.get("ci", "舒適")
        icon = get_weather_icon(wx)
        
        popup_html = f"""
        <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; width: 170px; padding: 4px;">
            <div style="font-size: 16px; font-weight: 700; color: #1E293B; margin-bottom: 4px; display: flex; align-items: center; justify-content: space-between;">
                <span>{loc_name}</span>
                <span style="font-size: 11px; background: {color}; color: white; padding: 2px 6px; border-radius: 9999px;">{region}</span>
            </div>
            <div style="font-size: 14px; margin-bottom: 4px; color: #475569;">
                {icon} <strong>{wx}</strong>
            </div>
            <div style="font-size: 13px; color: #0F172A; margin-bottom: 2px;">
                🌡️ <strong>{min_t}°C ~ {max_t}°C</strong>
            </div>
            <div style="font-size: 12px; color: #0284C7; margin-bottom: 2px;">
                💧 降雨機率: <strong>{pop}%</strong>
            </div>
            <div style="font-size: 11px; color: #64748B;">
                🛋️ {ci}
            </div>
        </div>
        """
        
        # Custom HTML div marker showing temperature badge
        icon_html = f"""
        <div style="
            background-color: {color};
            color: white;
            border-radius: 18px;
            padding: 2px 6px;
            font-size: 11px;
            font-weight: 700;
            box-shadow: 0 2px 6px rgba(0,0,0,0.3);
            text-align: center;
            white-space: nowrap;
            border: 2px solid white;
            transform: translate(-50%, -50%);
            cursor: pointer;
        ">
            {loc_name[:2]} {int(max_t)}°
        </div>
        """
        
        folium.Marker(
            location=[lat, lon],
            popup=folium.Popup(popup_html, max_width=220),
            tooltip=f"{loc_name}: {wx}, {min_t}~{max_t}°C, 降雨機率 {pop}%",
            icon=folium.DivIcon(html=icon_html)
        ).add_to(m)

    return m
