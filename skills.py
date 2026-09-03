import re
import json
import os
import webbrowser
import requests
from datetime import datetime, timedelta
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


def tell_joke() -> str:
    jokes = [
        "Why don't scientists trust atoms? Because they make up everything!",
        "Why did the Python programmer need glasses? Because he couldn't C#.",
        "Why do programmers prefer dark mode? Because light attracts bugs!",
        "Why did the developer go broke? Because he used up all his cache.",
        "How many programmers does it take to change a light bulb? None, that's a hardware problem.",
    ]
    import random
    return random.choice(jokes)


# -------------------------
# Reminders
# -------------------------
REMINDERS_FILE = "reminders.json"


def load_reminders() -> list:
    if os.path.exists(REMINDERS_FILE):
        try:
            with open(REMINDERS_FILE, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []
    return []


def save_reminders(reminders: list):
    with open(REMINDERS_FILE, "w") as f:
        json.dump(reminders, f, indent=2)


def parse_reminder_time(time_str: str) -> datetime | None:
    now = datetime.now()
    time_str = time_str.lower().strip()

    # "in X minutes/hours"
    match = re.match(r"in\s+(\d+)\s+(minute|min|hour|hr)s?", time_str)
    if match:
        amount = int(match.group(1))
        unit = match.group(2)
        if unit.startswith("hour") or unit.startswith("hr"):
            return now + timedelta(hours=amount)
        return now + timedelta(minutes=amount)

    # "at HH:MM" (24h)
    match = re.match(r"at\s+(\d{1,2}):(\d{2})", time_str)
    if match:
        h, m = int(match.group(1)), int(match.group(2))
        target = now.replace(hour=h, minute=m, second=0, microsecond=0)
        if target <= now:
            target += timedelta(days=1)
        return target

    # "at X AM/PM" or "at X:Y AM/PM"
    match = re.match(r"at\s+(\d{1,2})(?::(\d{2}))?\s*(am|pm)", time_str)
    if match:
        h = int(match.group(1))
        m = int(match.group(2) or 0)
        ampm = match.group(3)
        if ampm == "pm" and h != 12:
            h += 12
        elif ampm == "am" and h == 12:
            h = 0
        target = now.replace(hour=h, minute=m, second=0, microsecond=0)
        if target <= now:
            target += timedelta(days=1)
        return target

    # "tomorrow at ..."
    if "tomorrow" in time_str:
        match = re.search(r"at\s+(\d{1,2})(?::(\d{2}))?\s*(am|pm)?", time_str)
        if match:
            h = int(match.group(1))
            m = int(match.group(2) or 0)
            ampm = match.group(3)
            if ampm:
                if ampm == "pm" and h != 12:
                    h += 12
                elif ampm == "am" and h == 12:
                    h = 0
            target = (now + timedelta(days=1)).replace(hour=h, minute=m, second=0, microsecond=0)
            return target

    return None


def add_reminder(task: str, time_str: str) -> str:
    target_time = parse_reminder_time(time_str)
    if not target_time:
        return "Sorry, I couldn't understand the time. Try saying 'in 5 minutes' or 'at 3 PM'."

    reminders = load_reminders()
    reminders.append({
        "task": task,
        "time": target_time.isoformat(),
        "created": datetime.now().isoformat()
    })
    save_reminders(reminders)

    time_display = target_time.strftime("%I:%M %p").lstrip("0")
    if target_time.date() == datetime.now().date():
        return f"Reminder set for today at {time_display}: {task}"
    else:
        return f"Reminder set for {target_time.strftime('%B %d')} at {time_display}: {task}"


def get_reminders() -> str:
    reminders = load_reminders()
    if not reminders:
        return "You have no reminders set."

    lines = ["Your reminders:"]
    now = datetime.now()
    for i, r in enumerate(reminders, 1):
        try:
            t = datetime.fromisoformat(r["time"])
            if t.date() == now.date():
                time_str = f"today at {t.strftime('%I:%M %p').lstrip('0')}"
            elif t.date() == (now + timedelta(days=1)).date():
                time_str = f"tomorrow at {t.strftime('%I:%M %p').lstrip('0')}"
            else:
                time_str = t.strftime("%B %d at %I:%M %p").lstrip("0")
            lines.append(f"{i}. {r['task']} - {time_str}")
        except (KeyError, ValueError):
            lines.append(f"{i}. {r.get('task', 'Unknown')} - time unknown")

    return "\n".join(lines)


def cancel_reminder(task: str) -> str:
    reminders = load_reminders()
    task_lower = task.lower()

    for i, r in enumerate(reminders):
        if task_lower in r.get("task", "").lower():
            removed = reminders.pop(i)
            save_reminders(reminders)
            return f"Cancelled reminder: {removed['task']}"

    return f"No reminder found matching '{task}'."


def check_reminders() -> list:
    reminders = load_reminders()
    now = datetime.now()
    due = []
    remaining = []

    for r in reminders:
        try:
            t = datetime.fromisoformat(r["time"])
            if t <= now:
                due.append(r)
            else:
                remaining.append(r)
        except (KeyError, ValueError):
            remaining.append(r)

    if due:
        save_reminders(remaining)

    return due