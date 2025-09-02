import requests
import paho.mqtt.client as mqtt
import time
import json
import os

# === Konfigurasi API OpenWeatherMap ===
API_KEY = os.getenv("API_KEY", "YOUR_API_KEY")
LAT = -7.755284
LON = 112.540545
URL = f"https://api.openweathermap.org/data/2.5/weather?lat={LAT}&lon={LON}&appid={API_KEY}&units=metric"

# === Konfigurasi MQTT Broker ===
BROKER = "broker.emqx.io"   # ganti sesuai broker kamu
PORT = 1883
TOPICS = {
    "cuaca": "/wheaterstation/cuaca",
    "suhu": "/wheaterstation/Suhuudara",
    "kelembapan": "/wheaterstation/kelembapanudara",
    "tekanan": "/wheaterstation/Tekanan",
    "lux": "/wheaterstation/intensitascahaya",
    "curah": "/wheaterstation/curahhujan",
    "angin_ms": "/wheaterstation/kecepatanmeterperdetik",
    "angin_kmh": "/wheaterstation/kecepatankilometerperjam"
}

# === MQTT Client Setup ===
client = mqtt.Client(protocol=mqtt.MQTTv311)
client.connect(BROKER, PORT, 60)

last_fetch = 0
last_data = {}

try:
    while True:
        now = time.time()

        # Request data dari API tiap 2 menit sekali
        if now - last_fetch >= 120:
            response = requests.get(URL)
            data = response.json()
            last_fetch = now

            # === Parsing Data ===
            cuaca = data["weather"][0]["description"]
            temperature = data["main"]["temp"]
            humidity = data["main"]["humidity"]
            pressure = data["main"]["pressure"]
            wind_speed_ms = data["wind"]["speed"]
            wind_speed_kmh = round(wind_speed_ms * 3.6, 2)

            lux = data["clouds"]["all"]
            curah_hujan = data.get("rain", {}).get("1h", 0.0)

            last_data = {
                "cuaca": cuaca,
                "suhu": temperature,
                "kelembapan": humidity,
                "tekanan": pressure,
                "lux": lux,
                "curah": curah_hujan,
                "angin_ms": wind_speed_ms,
                "angin_kmh": wind_speed_kmh,
                "waktu": time.strftime("%Y-%m-%d %H:%M:%S")
            }

            print("Data baru diambil dari API:", json.dumps(last_data, indent=2))

        # Update ke MQTT realtime (meskipun datanya sama)
        if last_data:
            for key, value in last_data.items():
                if key in TOPICS:
                    client.publish(TOPICS[key], str(value))

            print("Data dipublish ke MQTT:", last_data["waktu"])

        time.sleep(5)  # publish tiap 5 detik

except KeyboardInterrupt:
    print("Program dihentikan manual")
    client.disconnect()
