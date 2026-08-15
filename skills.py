import re
import webbrowser
import requests
from urllib.parse import quote_plus

# -------------------------
# Weather
# -------------------------
WEATHER_CODES = {
    0: "clear sky", 1: "mainly clear", 2: "partly cloudy", 3: "overcast",
    45: "foggy", 48: "dense fog", 51: "light drizzle", 53: "moderate drizzle",
    55: "heavy drizzle", 61: "light rain", 63: "moderate rain", 65: "heavy rain",
    71: "light snow", 73: "moderate snow", 75: "heavy snow",
    95: "thunderstorm", 99: "severe thunderstorm",
}


def get_weather(city: str = "Solapur") -> str:
    try:
        geo = requests.get(
            f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1",
            timeout=8,
        ).json()
        if not geo.get("results"):
            return f"Sorry, I couldn't find weather data for {city}."
        lat = geo["results"][0]["latitude"]
        lon = geo["results"][0]["longitude"]

        weather = requests.get(
            f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true",
            timeout=8,
        ).json().get("current_weather")
        if not weather:
            return f"Weather data for {city} is currently unavailable."

        desc = WEATHER_CODES.get(weather["weathercode"], "unusual conditions")
        return (
            f"The current weather in {city} is {desc}, "
            f"with a temperature of {weather['temperature']}°C "
            f"and wind speed of {weather['windspeed']} km/h."
        )
    except Exception as e:
        return f"Sorry, something went wrong while fetching weather: {e}"

# -------------------------
# YouTube
# -------------------------
def play_youtube(song: str):
    if song:
        webbrowser.open(f"https://www.youtube.com/results?search_query={quote_plus(song)}")


def open_youtube(query: str = ""):
    if query:
        webbrowser.open(f"https://www.youtube.com/results?search_query={quote_plus(query)}")
    else:
        webbrowser.open("https://www.youtube.com")

# -------------------------
# Google
# -------------------------
def search_google(query: str):
    if query:
        webbrowser.open(f"https://www.google.com/search?q={quote_plus(query)}")


def show_image(query: str):
    if query:
        webbrowser.open(f"https://www.google.com/search?tbm=isch&q={quote_plus(query)}")


def strip_article(text: str) -> str:
    for article in ["a ", "an ", "the "]:
        if text.lower().startswith(article):
            return text[len(article):].strip()
    return text


def find_city(command: str) -> str:
    match = re.search(r"weather\s+(?:in|at|for|of)\s+([a-zA-Z\s]+)", command.lower())
    if match:
        return strip_article(match.group(1).strip())
    return "Solapur"