# 🌤️ Taiwan Weather Forecast Web App (台灣天氣預報 Web 應用)

> 🚀 **打造你的 AI Coding Agent：Antigravity × Gemini × GitHub**  
> 煥哥教學示範專案 — HW1: CWA Weather Forecast using AI Agent

![Antigravity](https://img.shields.io/badge/AI_IDE-Antigravity-blue?style=for-the-badge)
![Model](https://img.shields.io/badge/AI_Model-Gemini-4285F4?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.37+-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-Database-003B57?style=for-the-badge&logo=sqlite&logoColor=white)

---

## 📌 專案簡介

本專案使用 **Antigravity IDE** 與 **Gemini** 透過 **Vibe Coding（自然語言對話開發）** 實作。串接交通部**中央氣象署（CWA）開放資料 API**、**SQLite 本地資料庫**與 **Streamlit 視覺化框架**，打造全台灣 22 縣市即時天氣預報與互動地圖應用。

---

## ✨ 核心特色與功能

1. ⚡ **即時 CWA API 串接**：
   - 串接中央氣象署 `F-C0032-001`（一般天氣預報 - 今明36小時天氣預報）。
   - 支援即時 API Key 輸入與自動備援（Demo Mode），未設定金鑰也能無縫預覽。
2. 🗺️ **Folium 台灣互動地圖**：
   - 台灣全區地圖縮放、標籤與各縣市氣溫徽章。
   - 點擊標記即可查看天氣現象、溫度區間、降雨機率與舒適度指數。
3. 📊 **生活圈概況卡片（北部 / 中部 / 南部 / 東部 / 外島）**：
   - 即時計算各區域最高溫、最低溫與平均降雨機率。
4. 📈 **Plotly 動態圖表**：
   - 各縣市氣溫範圍（最低 ~ 最高溫）堆疊長條圖。
   - 降雨機率排行榜。
5. 💾 **SQLite 資料庫持久化**：
   - 自動將氣象資料建立索引並儲存於本地 `data/weather.db`。
   - 支援將快取資料即時匯出為 CSV。

---

## 📂 專案架構

```text
ANTIGRAVITY HW/
├── app.py               # Streamlit 主程式與 UI 儀表板
├── src/
│   ├── cwa_api.py       # 中央氣象署 API 串接與數據清洗
│   ├── database.py      # SQLite 資料庫管理與彙總查詢
│   └── map_utils.py     # Folium 台灣互動地圖視覺化模組
├── data/
│   └── weather.db       # SQLite 本地資料庫
├── requirements.txt     # 相依套件清單
├── .gitignore           # Git 忽略設定
└── README.md            # 專案說明文件
```

---

## 🛠️ 安裝與啟動教學

### 1. 安裝套件
確保已安裝 Python 3.10+，並在終端機執行：
```bash
pip install -r requirements.txt
```

### 2. 啟動應用程式
```bash
streamlit run app.py
```
啟動後瀏覽器會自動開啟 `http://localhost:8501`。

---

## 🔑 取得中央氣象署 CWA API 授權碼
1. 前往 [中央氣象署開放資料平臺](https://opendata.cwa.gov.tw/)。
2. 註冊並登入會員。
3. 點選「取得授權碼」並複製您的專屬授權金鑰。
4. 在網頁側邊欄輸入授權碼，點擊「🔄 更新資料」即可無縫切換為官方即時資料！

---

## 🏆 Vibe Coding 實作流程

- [x] **Step 1~2**: 下載 Antigravity IDE 並啟用 Gemini
- [x] **Step 3~6**: 建立專案、建立 GitHub Repository 並透過 AI 自動連線
- [x] **Step 7**: Vibe Coding 規劃架構與需求
- [x] **Step 8**: AI 產生程式碼並於本地進行執行與測試
- [x] **Step 9**: 持續迭代與優化（加入 Folium 互動地圖、生活圈卡片、Plotly 圖表）
- [x] **Step 10**: 版本控制 Commit & Push 至 GitHub 儲存庫
