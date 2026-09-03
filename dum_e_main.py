import asyncio
import threading
import re
from datetime import datetime
import tkinter as tk

from brain import brain
from io_manager import speak, mic_listener, selected_voice
from ui import FuturisticGUI
from skills import (
    get_weather, open_youtube, search_google, show_image, find_city,
    tell_joke, add_reminder, get_reminders, cancel_reminder, check_reminders
)

awake_mode = True

# -------------------------
# Response helper
# -------------------------
def respond(gui, message):
    gui.add_message(message, sender="assistant")
    gui.set_state("Speaking")
    asyncio.run(speak(message, selected_voice))
    gui.set_state("Listening")

# -------------------------
# Background reminder checker
# -------------------------
def reminder_checker(gui):
    while True:
        try:
            due = check_reminders()
            for r in due:
                task = r.get("task", "something")
                message = f"Reminder: {task}"
                gui.add_message(message, sender="assistant")
                gui.set_state("Speaking")
                asyncio.run(speak(message, selected_voice))
                gui.set_state("Listening")
        except Exception as e:
            print(f"Reminder checker error: {e}")
        threading.Event().wait(timeout=30)

# -------------------------
# Intent routing
# -------------------------
def route_command(command, gui):
    global awake_mode

    c = command.lower().replace("-", " ").replace("  ", " ").strip()

    # Sleep / Wake
    if any(t in c for t in ["sleep dummy", "go to sleep", "sleep mode"]):
        awake_mode = False
        respond(gui, "Sleep mode activated. Say 'dummy' to wake me up again.")
        return True
    if not awake_mode and any(t in c for t in ["dummy", "wake up", "turn on dummy", "hey dummy"]):
        awake_mode = True
        respond(gui, "I am listening, Sir.")
        return True
    if not awake_mode:
        return True

    # Exit
    if any(t in c for t in [
        "shutdown", "shut down", "close the program", "turn off", "goodbye",
        "good bye", "bye", "good night",
    ]):
        hour = datetime.now().hour
        msg = "Good night Sir" if (hour >= 21 or hour < 5) else "Goodbye Sir, have a great day"
        respond(gui, msg)
        gui.root.after(1200, gui._close)
        return True

    # Identity
    if any(t in c for t in ["who are you", "your name", "what is your name", "u ai", "u bot"]):
        respond(gui, "I am Deep Universal Mind Electric — DUM-E for short, but you can call me Dummy!")
        return True

    # Creator
    if any(t in c for t in ["who made you", "who created you", "who built you", "your creator", "who is your maker"]):
        respond(gui, "I was designed and built from scratch by Khizar Sagri, an Indian programmer.")
        return True

    # Purpose
    if any(t in c for t in ["what is your purpose", "why do you exist", "what do you do", "your role", "what's your job"]):
        respond(gui, (
            "I am an artificial intelligence assistant built to make life easier. "
            "I can answer questions, fetch weather, search the web, open media, "
            "and evolve with your needs — all powered by fast, free AI."
        ))
        return True

    # Weather
    if "weather" in c:
        gui.set_state("Busy")
        city = find_city(c)
        respond(gui, get_weather(city))
        return True

    # Time / Date
    if "time" in c:
        now = datetime.now()
        h = now.hour % 12 or 12
        respond(gui, f"Sir, the current time is {h}:{now.minute:02d} {'AM' if now.hour < 12 else 'PM'}.")
        return True
    if "date" in c or ("today" in c and "what" in c):
        now = datetime.now()
        respond(gui, f"Today is {now.strftime('%A')}, {now.day} {now.strftime('%B')} {now.year}.")
        return True

    # Images
    for prefix in ["image of ", "photo of ", "picture of "]:
        if prefix in c:
            q = c.split(prefix, 1)[1].strip()
            show_image(q)
            gui.add_message(f"DUM-E: Opening image results for {q}", sender="assistant")
            return True

    # Joke
    if any(t in c for t in ["joke", "tell me a joke", "make me laugh"]):
        respond(gui, tell_joke())
        return True

    # YouTube
    if "youtube" in c:
        q = c.split("youtube", 1)[-1]
        for word in ["play", "search", "on", "for", "open"]:
            q = q.replace(word, " ").strip()
        gui.set_state("Busy")
        open_youtube(q)
        return True

    # Google
    if "google" in c:
        q = c.split("google", 1)[-1]
        for word in ["search", "on", "for", "open"]:
            q = q.replace(word, " ").strip()
        gui.set_state("Busy")
        search_google(q)
        return True

    # Reminders - list
    if any(t in c for t in ["what are my reminders", "list reminders", "show reminders", "my reminders"]):
        respond(gui, get_reminders())
        return True

    # Reminders - cancel
    if any(t in c for t in ["cancel reminder", "remove reminder"]):
        task = c.split("reminder", 1)[-1].strip()
        for word in ["cancel", "remove"]:
            task = task.replace(word, "").strip()
        respond(gui, cancel_reminder(task))
        return True

    # Reminders - add (remind me to ... at ...)
    remind_match = re.search(r"(?:remind me to|set reminder for)\s+(.+?)\s+(?:at|in)\s+(.+)", c)
    if remind_match:
        task = remind_match.group(1).strip()
        time_str = remind_match.group(2).strip()
        respond(gui, add_reminder(task, time_str))
        return True

    return False

def handle_typed(command, gui):
    if route_command(command, gui):
        return
    gui.set_state("Thinking")
    reply = brain.think(command)
    respond(gui, reply)

# -------------------------
# Runner
# -------------------------
def start_dum_e(gui):
    now = datetime.now()
    greeting = (
        "Good morning Sir." if 5 <= now.hour < 12 else
        "Good afternoon Sir." if now.hour < 17 else
        "Good evening Sir."
    )
    welcome = f"{greeting} Today is {now.strftime('%A')}, {now.day} {now.strftime('%B')} {now.year}. How can I help you Sir?"
    respond(gui, welcome)

    while True:
        command = asyncio.run(mic_listener(print_prompt=False))
        if not command:
            continue

        gui.add_message(command, sender="user")

        if route_command(command, gui):
            continue

        # Fall back to the AI brain
        gui.set_state("Thinking")
        reply = brain.think(command)
        respond(gui, reply)

# -------------------------
# Main
# -------------------------
if __name__ == "__main__":
    root = tk.Tk()
    gui = FuturisticGUI(root)
    gui.on_command = lambda c: handle_typed(c, gui)
    threading.Thread(target=start_dum_e, args=(gui,), daemon=True).start()
    threading.Thread(target=reminder_checker, args=(gui,), daemon=True).start()
    root.mainloop()