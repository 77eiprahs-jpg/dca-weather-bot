import requests
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

STATION = "KDCA"
LAT = 38.8512
LON = -77.0402
SHEET_NAME = "DCA Weather Live Log"

scope = ["https://spreadsheets.google.com/feeds",
         "https://www.googleapis.com/auth/drive"]

creds = ServiceAccountCredentials.from_json_keyfile_name(
    "credentials.json", scope)

client = gspread.authorize(creds)
sheet = client.open(SHEET_NAME).sheet1

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

def collect():
    timestamp = str(datetime.utcnow())
    current_temp = nws_observation()
    forecast_high = nws_forecast_high()
    sheet.append_row([timestamp, current_temp, forecast_high])

if __name__ == "__main__":
    collect()
