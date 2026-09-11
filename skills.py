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


# -------------------------
# Notes / Tasks
# -------------------------
NOTES_FILE = "notes.json"


def load_notes() -> list:
    if os.path.exists(NOTES_FILE):
        try:
            with open(NOTES_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data if isinstance(data, list) else []
        except (json.JSONDecodeError, IOError):
            return []
    return []


def save_notes(notes: list):
    with open(NOTES_FILE, "w", encoding="utf-8") as f:
        json.dump(notes, f, indent=2, ensure_ascii=False)


def add_note(text: str) -> str:
    text = text.strip().strip(".").strip()
    if not text:
        return "I didn't catch what to note down. Try saying 'take a note buy milk tomorrow'."
    notes = load_notes()
    new_id = (max((n.get("id", 0) for n in notes), default=0) + 1)
    notes.append({
        "id": new_id,
        "text": text,
        "created": datetime.now().isoformat(),
    })
    save_notes(notes)
    return f"Note saved as #{new_id}: {text}"


def get_notes() -> str:
    notes = load_notes()
    if not notes:
        return "You have no notes yet. Say 'take a note ...' to add one."
    lines = [f"Your notes ({len(notes)}):"]
    for n in notes:
        try:
            dt = datetime.fromisoformat(n["created"])
            when = dt.strftime("%b %d %I:%M %p").lstrip("0")
        except Exception:
            when = "unknown time"
        lines.append(f"{n['id']}. {n['text']}  [{when}]")
    return "\n".join(lines)


def delete_note(query: str) -> str:
    notes = load_notes()
    if not notes:
        return "You have no notes to delete."
    query = query.strip().lower()
    if not query:
        return "Tell me which note to delete — say 'delete note 2' or 'delete note buy milk'."

    # Try numeric id first
    try:
        qid = int(re.search(r"\d+", query).group())
        for i, n in enumerate(notes):
            if n.get("id") == qid:
                removed = notes.pop(i)
                save_notes(notes)
                return f"Deleted note #{qid}: {removed['text']}"
    except Exception:
        pass

    # Text match
    for i, n in enumerate(notes):
        if query in n.get("text", "").lower():
            removed = notes.pop(i)
            save_notes(notes)
            return f"Deleted note #{removed['id']}: {removed['text']}"

    return f"No note found matching '{query}'. Say 'show notes' to see all notes."


def search_notes(query: str) -> str:
    notes = load_notes()
    query = query.strip().lower()
    if not query:
        return "Tell me what to search for — say 'search notes for milk'."
    if not notes:
        return "You have no notes yet."
    hits = [n for n in notes if query in n.get("text", "").lower()]
    if not hits:
        return f"No notes found matching '{query}'."
    lines = [f"Found {len(hits)} note(s) for '{query}':"]
    for n in hits:
        lines.append(f"{n['id']}. {n['text']}")
    return "\n".join(lines)


def clear_notes() -> str:
    notes = load_notes()
    if not notes:
        return "You have no notes to clear."
    save_notes([])
    return f"Cleared all {len(notes)} note(s)."


def edit_note(note_id: int, new_text: str) -> str:
    notes = load_notes()
    new_text = new_text.strip()
    if not new_text:
        return "New text cannot be empty."
    for n in notes:
        if n.get("id") == note_id:
            old = n["text"]
            n["text"] = new_text
            n["updated"] = datetime.now().isoformat()
            save_notes(notes)
            return f"Updated note #{note_id}: '{old}' -> '{new_text}'"
    return f"No note found with id #{note_id}."


# -------------------------
# Calculator + Unit Converter
# -------------------------
import ast
import operator as _op

_SAFE_OPS = {
    ast.Add: _op.add, ast.Sub: _op.sub, ast.Mult: _op.mul,
    ast.Div: _op.truediv, ast.Mod: _op.mod, ast.Pow: _op.pow,
    ast.USub: _op.neg, ast.UAdd: _op.pos,
}


def _safe_eval(node):
    if isinstance(node, ast.Expression):
        return _safe_eval(node.body)
    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return node.value
        raise ValueError("Invalid number")
    if isinstance(node, ast.BinOp) and type(node.op) in _SAFE_OPS:
        left = _safe_eval(node.left)
        right = _safe_eval(node.right)
        return _SAFE_OPS[type(node.op)](left, right)
    if isinstance(node, ast.UnaryOp) and type(node.op) in _SAFE_OPS:
        return _SAFE_OPS[type(node.op)](_safe_eval(node.operand))
    raise ValueError("Unsupported expression")


def _format_number(value: float) -> str:
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    rounded = round(value, 6)
    if isinstance(rounded, float) and rounded.is_integer():
        return str(int(rounded))
    return str(rounded)


def _words_to_math(text: str) -> str:
    t = text.lower().strip()
    replacements = [
        (r"\bmultiplied by\b", " * "), (r"\bmultiply by\b", " * "),
        (r"\bdivided by\b", " / "), (r"\bdivide by\b", " / "),
        (r"\bto the power of\b", " ** "), (r"\bto the power\b", " ** "),
        (r"\bpower\b", " ** "), (r"\bsquared\b", " ** 2 "),
        (r"\bcubed\b", " ** 3 "), (r"\btimes\b", " * "),
        (r"\bplus\b", " + "), (r"\bminus\b", " - "),
        (r"\bover\b", " / "), (r"\bmodulo\b", " % "),
        (r"\bmod\b", " % "), (r"\bx\b", " * "),
        (r"÷", " / "), (r"×", " * "), (r"−", " - "),
    ]
    for pattern, repl in replacements:
        t = re.sub(pattern, repl, t)
    # "15 percent of 200" -> "(15/100*200)"
    t = re.sub(
        r"(\d+(?:\.\d+)?)\s*percent\s+of\s+(\d+(?:\.\d+)?)",
        r"(\1/100*\2)", t,
    )
    t = re.sub(r"(\d+(?:\.\d+)?)\s*%\s*of\s+(\d+(?:\.\d+)?)", r"(\1/100*\2)", t)
    t = re.sub(r"(\d+(?:\.\d+)?)\s*%", r"(\1/100)", t)
    return t


def _extract_math(expr: str) -> str | None:
    """Pull the math-looking portion out of a sentence, or None."""
    # keep only chars that can appear in math
    m = re.search(r"[-+*/%().\d\s*a-z]+", expr)
    if not m:
        return None
    candidate = m.group(0).strip()
    # must contain at least one digit and one operator
    if not re.search(r"\d", candidate):
        return None
    if not re.search(r"[+\-*/%()^]", candidate):
        return None
    candidate = candidate.replace("^", "**").strip()
    # reject if letters other than e (sci notation) remain
    if re.search(r"[a-df-zA-DF-Z]", candidate):
        return None
    if not re.match(r"^[\d\s+\-*/%().**eE]+$", candidate):
        return None
    return candidate


_LENGTH_TO_M = {
    "km": 1000.0, "kilometer": 1000.0, "kilometers": 1000.0, "kilometre": 1000.0,
    "m": 1.0, "meter": 1.0, "meters": 1.0, "metre": 1.0, "metres": 1.0,
    "cm": 0.01, "centimeter": 0.01, "centimeters": 0.01,
    "mm": 0.001, "millimeter": 0.001, "millimeters": 0.001,
    "mi": 1609.344, "mile": 1609.344, "miles": 1609.344,
    "ft": 0.3048, "foot": 0.3048, "feet": 0.3048,
    "in": 0.0254, "inch": 0.0254, "inches": 0.0254,
    "yd": 0.9144, "yard": 0.9144, "yards": 0.9144,
}
_weight_TO_KG = {
    "kg": 1.0, "kilogram": 1.0, "kilograms": 1.0, "kilo": 1.0, "kilos": 1.0,
    "g": 0.001, "gram": 0.001, "grams": 0.001,
    "lb": 0.45359237, "lbs": 0.45359237, "pound": 0.45359237, "pounds": 0.45359237,
    "oz": 0.028349523125, "ounce": 0.028349523125, "ounces": 0.028349523125,
}


def _convert_units(command: str) -> str | None:
    m = re.search(
        r"convert\s+(-?\d+(?:\.\d+)?)\s*([a-z°º]+)\s+(?:to|in|into)\s+([a-z°º]+)",
        command.lower(),
    )
    if not m:
        return None
    value = float(m.group(1))
    src = m.group(2).strip("°º.").lower()
    dst = m.group(3).strip("°º.").lower()
    src_c = src.replace("celsius", "c").replace("fahrenheit", "f").replace("kelvin", "k")
    dst_c = dst.replace("celsius", "c").replace("fahrenheit", "f").replace("kelvin", "k")

    # Temperature
    if src_c in ("c", "f", "k") and dst_c in ("c", "f", "k"):
        if src_c == "c":
            celsius = value
        elif src_c == "f":
            celsius = (value - 32) * 5 / 9
        else:
            celsius = value - 273.15
        if dst_c == "c":
            out = celsius
        elif dst_c == "f":
            out = celsius * 9 / 5 + 32
        else:
            out = celsius + 273.15
        return f"{_format_number(value)} {src} is {_format_number(out)} {dst}."

    # Length
    if src in _LENGTH_TO_M and dst in _LENGTH_TO_M:
        meters = value * _LENGTH_TO_M[src]
        out = meters / _LENGTH_TO_M[dst]
        return f"{_format_number(value)} {src} is {_format_number(out)} {dst}."

    # Weight
    if src in _weight_TO_KG and dst in _weight_TO_KG:
        kg = value * _weight_TO_KG[src]
        out = kg / _weight_TO_KG[dst]
        return f"{_format_number(value)} {src} is {_format_number(out)} {dst}."

    return f"Sorry, I can't convert {src} to {dst} yet."


def calculate_expression(command: str) -> str | None:
    """Try to evaluate a voice math query. Returns answer string or None."""
    converted = _convert_units(command)
    if converted is not None:
        return converted

    text = command.lower().strip()
    # strip leading trigger phrases
    for prefix in ["calculate ", "compute ", "solve ", "evaluate ",
                   "how much is ", "what is ", "what's ", "whats "]:
        if text.startswith(prefix):
            text = text[len(prefix):].strip()
            break
    else:
        # also strip mid-sentence triggers like "hey dummy calculate ..."
        for trig in ["calculate ", "compute ", "solve "]:
            if trig in text:
                text = text.split(trig, 1)[-1].strip()
                break

    math_text = _words_to_math(text)
    candidate = _extract_math(math_text)
    if not candidate:
        return None
    try:
        tree = ast.parse(candidate, mode="eval")
        result = _safe_eval(tree)
        if isinstance(result, (int, float)):
            return f"The answer is {_format_number(float(result))}."
        return None
    except ZeroDivisionError:
        return "Anything divided by zero is undefined, Sir."
    except Exception:
        return None