"""
CWA (Central Weather Administration / 交通部中央氣象署) API client.
Dataset: F-C0032-001 (一般天氣預報-今明36小時天氣預報)
"""
import requests
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple

CWA_API_URL = "https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-C0032-001"

COUNTY_REGIONS = {
    # 北部
    "基隆市": "北部", "臺北市": "北部", "新北市": "北部", "桃園市": "北部",
    "新竹市": "北部", "新竹縣": "北部", "宜蘭縣": "北部",
    # 中部
    "苗栗縣": "中部", "臺中市": "中部", "彰化縣": "中部", "南投縣": "中部", "雲林縣": "中部",
    # 南部
    "嘉義市": "南部", "嘉義縣": "南部", "臺南市": "南部", "高雄市": "南部", "屏東縣": "南部",
    # 東部
    "花蓮縣": "東部", "臺東縣": "東部",
    # 外島
    "澎湖縣": "外島", "金門縣": "外島", "連江縣": "外島"
}

COUNTY_COORDINATES = {
    "基隆市": (25.1283, 121.7419),
    "臺北市": (25.0375, 121.5637),
    "新北市": (25.0116, 121.4658),
    "桃園市": (24.9936, 121.3010),
    "新竹市": (24.8138, 120.9675),
    "新竹縣": (24.8387, 121.0177),
    "苗栗縣": (24.5602, 120.8214),
    "臺中市": (24.1477, 120.6736),
    "彰化縣": (24.0518, 120.5161),
    "南投縣": (23.9609, 120.9719),
    "雲林縣": (23.7092, 120.4313),
    "嘉義市": (23.4800, 120.4491),
    "嘉義縣": (23.4518, 120.2555),
    "臺南市": (22.9997, 120.2270),
    "高雄市": (22.6273, 120.3014),
    "屏東縣": (22.5519, 120.5487),
    "宜蘭縣": (24.7021, 121.7377),
    "花蓮縣": (23.9872, 121.6016),
    "臺東縣": (22.7583, 121.1444),
    "澎湖縣": (23.5712, 119.5793),
    "金門縣": (24.4492, 118.3766),
    "連江縣": (26.1557, 119.9515)
}


def parse_cwa_json(data: dict) -> List[Dict[str, Any]]:
    """Parse raw CWA F-C0032-001 JSON into normalized flat records."""
    records = []
    locations = data.get("records", {}).get("location", [])
    
    for loc in locations:
        loc_name = loc.get("locationName", "")
        region = COUNTY_REGIONS.get(loc_name, "其他")
        
        elements = {}
        for elem in loc.get("weatherElement", []):
            elements[elem.get("elementName")] = elem.get("time", [])
            
        time_len = min(len(t) for t in elements.values()) if elements else 0
        
        for idx in range(time_len):
            wx_elem = elements.get("Wx", [{}])[idx]
            pop_elem = elements.get("PoP", [{}])[idx]
            mint_elem = elements.get("MinT", [{}])[idx]
            maxt_elem = elements.get("MaxT", [{}])[idx]
            ci_elem = elements.get("CI", [{}])[idx]
            
            start_time = wx_elem.get("startTime", "")
            end_time = wx_elem.get("endTime", "")
            wx_val = wx_elem.get("parameter", {}).get("parameterName", "晴時多雲")
            pop_val = int(pop_elem.get("parameter", {}).get("parameterName", "0") or 0)
            mint_val = float(mint_elem.get("parameter", {}).get("parameterName", "20.0") or 20.0)
            maxt_val = float(maxt_elem.get("parameter", {}).get("parameterName", "28.0") or 28.0)
            ci_val = ci_elem.get("parameter", {}).get("parameterName", "舒適")
            
            records.append({
                "location_name": loc_name,
                "region": region,
                "period_index": idx,
                "start_time": start_time,
                "end_time": end_time,
                "wx": wx_val,
                "pop": pop_val,
                "min_t": mint_val,
                "max_t": maxt_val,
                "ci": ci_val
            })
            
    return records


def get_demo_weather_records() -> List[Dict[str, Any]]:
    """Provide realistic high-fidelity mock weather data when API key is not yet set."""
    now = datetime.now()
    periods = [
        (now.strftime("%Y-%m-%d %H:00"), (now + timedelta(hours=12)).strftime("%Y-%m-%d %H:00")),
        ((now + timedelta(hours=12)).strftime("%Y-%m-%d %H:00"), (now + timedelta(hours=24)).strftime("%Y-%m-%d %H:00")),
        ((now + timedelta(hours=24)).strftime("%Y-%m-%d %H:00"), (now + timedelta(hours=36)).strftime("%Y-%m-%d %H:00")),
    ]
    
    mock_base = {
        # 北部
        "基隆市": ("陰短暫雨", 40, 18.0, 24.0, "稍有寒意至舒適"),
        "臺北市": ("多雲時晴", 20, 19.0, 26.0, "舒適"),
        "新北市": ("多雲短暫雨", 30, 19.0, 25.0, "舒適"),
        "桃園市": ("陰天", 20, 18.0, 25.0, "舒適"),
        "新竹市": ("晴時多雲", 10, 19.0, 26.0, "舒適"),
        "新竹縣": ("晴時多雲", 10, 18.0, 26.0, "舒適"),
        "宜蘭縣": ("陰短暫雨", 50, 18.0, 24.0, "稍有寒意至舒適"),
        # 中部
        "苗栗縣": ("晴時多雲", 10, 19.0, 27.0, "舒適至微熱"),
        "臺中市": ("晴天", 10, 20.0, 29.0, "舒適至微熱"),
        "彰化縣": ("晴天", 10, 20.0, 29.0, "舒適至微熱"),
        "南投縣": ("多雲午後短暫陣雨", 30, 18.0, 28.0, "舒適"),
        "雲林縣": ("晴天", 10, 20.0, 30.0, "舒適至悶熱"),
        # 南部
        "嘉義市": ("晴天", 10, 21.0, 30.0, "舒適至微熱"),
        "嘉義縣": ("晴天", 10, 21.0, 30.0, "舒適至微熱"),
        "臺南市": ("晴時多雲", 10, 22.0, 31.0, "微熱至悶熱"),
        "高雄市": ("晴天", 10, 23.0, 32.0, "微熱至悶熱"),
        "屏東縣": ("多雲時晴", 20, 23.0, 32.0, "微熱至悶熱"),
        # 東部
        "花蓮縣": ("多雲短暫雨", 30, 20.0, 27.0, "舒適"),
        "臺東縣": ("多雲短暫雨", 30, 21.0, 28.0, "舒適"),
        # 外島
        "澎湖縣": ("多雲時晴", 10, 22.0, 28.0, "舒適"),
        "金門縣": ("晴時多雲", 10, 18.0, 25.0, "舒適"),
        "連江縣": ("陰天", 20, 16.0, 22.0, "稍有寒意")
    }
    
    records = []
    for loc_name, (wx, pop, min_t, max_t, ci) in mock_base.items():
        region = COUNTY_REGIONS.get(loc_name, "其他")
        for idx, (st, et) in enumerate(periods):
            # slight variation per period
            temp_shift = idx * 0.5
            records.append({
                "location_name": loc_name,
                "region": region,
                "period_index": idx,
                "start_time": st,
                "end_time": et,
                "wx": wx if idx == 0 else ("多雲" if idx == 1 else wx),
                "pop": max(0, min(100, pop + (idx * 5 if "雨" in wx else -5))),
                "min_t": round(min_t - temp_shift, 1),
                "max_t": round(max_t + temp_shift, 1),
                "ci": ci
            })
            
    return records


def fetch_cwa_weather(api_key: str = "") -> Tuple[List[Dict[str, Any]], str, bool]:
    """
    Fetch weather forecasts from CWA API, fallback to demo dataset if key is invalid or absent.
    Returns: (records, status_message, is_live_api)
    """
    if not api_key:
        return get_demo_weather_records(), "使用示範數據（未輸入 CWA API Key）", False
        
    try:
        params = {
            "Authorization": api_key,
            "format": "JSON"
        }
        resp = requests.get(CWA_API_URL, params=params, timeout=10)
        
        if resp.status_code == 200:
            data = resp.json()
            if data.get("success") == "true":
                records = parse_cwa_json(data)
                if records:
                    return records, "成功串接 CWA 中央氣象署即時 API 資料！", True
                    
        return get_demo_weather_records(), f"API 呼叫未成功（HTTP {resp.status_code}），已切換至示範數據", False
    except Exception as e:
        return get_demo_weather_records(), f"連線至 CWA API 發生錯誤 ({str(e)})，已切換至示範數據", False
