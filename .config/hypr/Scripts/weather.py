import requests

weather_map = {
    # Clear & Cloudy
    0: "Clear sky ☀️",
    1: "Mainly clear 🌤️",
    2: "Partly cloudy ⛅",
    3: "Overcast ☁️",
    # Fog
    45: "Foggy 🌫️",
    48: "Depositing rime fog 🌫️",
    # Drizzle
    51: "Light drizzle 🌧️",
    53: "Moderate drizzle 🌧️",
    55: "Dense drizzle 🌧️",
    56: "Light freezing drizzle 🥶",
    57: "Dense freezing drizzle 🥶",
    # Rain
    61: "Slight rain 🌦️",
    63: "Moderate rain 🌧️",
    65: "Heavy rain ⛈️",
    66: "Light freezing rain 🧊",
    67: "Heavy freezing rain 🧊",
    # Snow
    71: "Slight snow fall ❄️",
    73: "Moderate snow fall ❄️",
    75: "Heavy snow fall ❄️",
    77: "Snow grains 🌨️",
    # Showers
    80: "Slight rain showers 🌦️",
    81: "Moderate rain showers 🌧️",
    82: "Violent rain showers ⛈️",
    85: "Slight snow showers 🌨️",
    86: "Heavy snow showers 🌨️",
    # Thunderstorms
    95: "Thunderstorm ⛈️",
    96: "Thunderstorm with slight hail ⛈️",
    99: "Thunderstorm with heavy hail ⛈️",
}

cityname = input("What is the cityname: ")

API_REQUEST = f"https://geocoding-api.open-meteo.com/v1/search?name={cityname}&count=1"

GET_API_REQUEST = requests.get(API_REQUEST)
data = GET_API_REQUEST.json()

if "results" in data:
    lat = data["results"][0]["latitude"]
    lon = data["results"][0]["longitude"]
    print(f"I found it! {cityname} is at Lat: {lat}, Lon: {lon}")

    WEATHER_API_REQUEST = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,weather_code&temperature_unit=fahrenheit"

    GET_WEATHER_API_REQUEST = requests.get(WEATHER_API_REQUEST)
    weather_data = GET_WEATHER_API_REQUEST.json()

    temp_f = weather_data["current"]["temperature_2m"]

    temp_c = (temp_f - 32) * 5 / 9

    # Use :.1f to round to one decimal place
    print(f"The Temperature in {cityname} is {temp_c:.1f}C")
    print(f"The Temperature in {cityname} is {temp_f:.1f}F")

    code = weather_data["current"]["weather_code"]
    status = weather_map.get(code, "Unknown Weather")

    print(f"Condition: {status}")

else:
    print("Couldn't find that city fuck you")
