import requests

API_KEY = "c817d2082fbcd5ec5fc83d342ca1a0d9"  

def get_weather(city_name):
    if not city_name:
        return {}

    try:
        url = "http://api.openweathermap.org/data/2.5/weather"
        params = {
            "q": city_name,
            "appid": API_KEY,
            "units": "imperial"
        }
        response = requests.get(url, params=params)
        data = response.json()

        if "main" not in data or "wind" not in data or "weather" not in data:
            return {}

        return {
            "temp": data["main"].get("temp", 0),
            "wind_mph": data["wind"].get("speed", 0),
            "conditions": data["weather"][0].get("description", "")
        }
    except Exception as e:
        print(f"Weather fetch error for {city_name}: {e}")
        return {}
