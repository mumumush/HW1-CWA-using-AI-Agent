"""
SQLite Database manager for Taiwan Weather Forecast application.
Stores CWA weather forecast data, historical records, and provides query functions.
"""
import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Any, Optional

DB_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
DEFAULT_DB_PATH = os.path.join(DB_DIR, 'weather.db')


def get_connection(db_path: str = DEFAULT_DB_PATH) -> sqlite3.Connection:
    """Ensure data directory exists and return database connection."""
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: str = DEFAULT_DB_PATH) -> None:
    """Create weather forecast table if not exists."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS weather_forecast (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fetch_time TEXT NOT NULL,
            location_name TEXT NOT NULL,
            region TEXT NOT NULL,
            period_index INTEGER NOT NULL,
            start_time TEXT NOT NULL,
            end_time TEXT NOT NULL,
            wx TEXT,
            pop INTEGER,
            min_t REAL,
            max_t REAL,
            ci TEXT,
            UNIQUE(location_name, start_time, end_time) ON CONFLICT REPLACE
        )
    ''')
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_weather_location 
        ON weather_forecast(location_name, period_index)
    ''')
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_weather_fetch 
        ON weather_forecast(fetch_time)
    ''')
    conn.commit()
    conn.close()


def save_forecast_records(records: List[Dict[str, Any]], db_path: str = DEFAULT_DB_PATH) -> int:
    """Save parsed weather forecast records into SQLite."""
    init_db(db_path)
    conn = get_connection(db_path)
    cursor = conn.cursor()
    
    count = 0
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    for r in records:
        cursor.execute('''
            INSERT INTO weather_forecast (
                fetch_time, location_name, region, period_index,
                start_time, end_time, wx, pop, min_t, max_t, ci
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(location_name, start_time, end_time) DO UPDATE SET
                fetch_time = excluded.fetch_time,
                region = excluded.region,
                period_index = excluded.period_index,
                wx = excluded.wx,
                pop = excluded.pop,
                min_t = excluded.min_t,
                max_t = excluded.max_t,
                ci = excluded.ci
        ''', (
            now_str,
            r.get('location_name'),
            r.get('region', '其他'),
            r.get('period_index', 0),
            r.get('start_time'),
            r.get('end_time'),
            r.get('wx'),
            r.get('pop'),
            r.get('min_t'),
            r.get('max_t'),
            r.get('ci')
        ))
        count += 1
        
    conn.commit()
    conn.close()
    return count


def get_latest_forecasts(period_index: int = 0, db_path: str = DEFAULT_DB_PATH) -> List[Dict[str, Any]]:
    """Retrieve the latest forecast for all locations for a specific time period."""
    init_db(db_path)
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM weather_forecast
        WHERE period_index = ?
        ORDER BY 
            CASE region
                WHEN '北部' THEN 1
                WHEN '中部' THEN 2
                WHEN '南部' THEN 3
                WHEN '東部' THEN 4
                ELSE 5
            END, location_name
    ''', (period_index,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_regional_summary(period_index: int = 0, db_path: str = DEFAULT_DB_PATH) -> List[Dict[str, Any]]:
    """Get min and max temperature aggregated by region (北部, 中部, 南部, 東部, 外島)."""
    init_db(db_path)
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT 
            region,
            ROUND(MIN(min_t), 1) as min_temp,
            ROUND(MAX(max_t), 1) as max_temp,
            ROUND(AVG(pop), 0) as avg_pop,
            COUNT(*) as county_count
        FROM weather_forecast
        WHERE period_index = ?
        GROUP BY region
        ORDER BY 
            CASE region
                WHEN '北部' THEN 1
                WHEN '中部' THEN 2
                WHEN '南部' THEN 3
                WHEN '東部' THEN 4
                WHEN '外島' THEN 5
                ELSE 6
            END
    ''', (period_index,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]
