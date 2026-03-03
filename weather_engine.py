import requests
import pandas as pd
from datetime import datetime
import os

STATION = "KDCA"
LAT = 38.8512
LON = -77.0402

LIVE_FILE = "DCA_live_log.csv"
MAX_FILE = "DCA_daily_max.csv"
REVISION_FILE = "DCA_forecast_revisions.csv"

def nws_observation():
    url = f"https://api.weather.gov/stations/{STATION}/observations/latest"
    data = requests.get(url).json()["properties"]
    temp_c = data["temperature"]["value"]
    return round((temp_c * 9/5) + 32, 1) if temp_c else None

def nws_forecast_high():
    points = requests.get(f"https://api.weather.gov/points/{LAT},{LON}").json()
    forecast_url = points["properties"]["forecast"]
    periods = requests.get(forecast_url).json()["properties"]["periods"]
    for p in periods:
        if p["isDaytime"]:
            return p["temperature"]

def update_daily_max(current_temp):
    today = datetime.utcnow().date()

    if os.path.exists(MAX_FILE):
        df = pd.read_csv(MAX_FILE)
        if str(today) in df["Date"].values:
            existing = df.loc[df["Date"] == str(today), "Official_Max_F"].values[0]
            if current_temp > existing:
                df.loc[df["Date"] == str(today), "Official_Max_F"] = current_temp
                df.to_csv(MAX_FILE, index=False)
            return

    new_row = pd.DataFrame([{
        "Date": str(today),
        "Official_Max_F": current_temp
    }])

    if os.path.exists(MAX_FILE):
        new_row.to_csv(MAX_FILE, mode='a', header=False, index=False)
    else:
        new_row.to_csv(MAX_FILE, index=False)

def detect_revision(current_forecast):
    if os.path.exists(REVISION_FILE):
        df = pd.read_csv(REVISION_FILE)
        last_forecast = df.iloc[-1]["Forecast_High_F"]
        if current_forecast != last_forecast:
            pd.DataFrame([{
                "Timestamp": datetime.utcnow(),
                "Forecast_High_F": current_forecast
            }]).to_csv(REVISION_FILE, mode='a', header=False, index=False)
    else:
        pd.DataFrame([{
            "Timestamp": datetime.utcnow(),
            "Forecast_High_F": current_forecast
        }]).to_csv(REVISION_FILE, index=False)

def collect():
    timestamp = datetime.utcnow()
    current_temp = nws_observation()
    forecast_high = nws_forecast_high()

    pd.DataFrame([{
        "Timestamp": timestamp,
        "Observed_Temp_F": current_temp,
        "Forecast_High_F": forecast_high
    }]).to_csv(
        LIVE_FILE,
        mode='a',
        header=not os.path.exists(LIVE_FILE),
        index=False
    )

    if current_temp:
        update_daily_max(current_temp)

    if forecast_high:
        detect_revision(forecast_high)

if __name__ == "__main__":
    collect()
