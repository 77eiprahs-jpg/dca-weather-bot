import time
from weather_engine import collect

while True:
    collect()
    time.sleep(1800)  # 30 minutes
