import asyncio
import threading
import re
from datetime import datetime
import tkinter as tk

from brain import brain
from io_manager import speak, mic_listener, set_voice, get_voice, VOICE_CATALOG
from ui import FuturisticGUI
from skills import (
    get_weather, open_youtube, search_google, show_image, find_city,
    tell_joke, add_reminder, get_reminders, cancel_reminder, check_reminders,
    add_note, get_notes, delete_note, search_notes, clear_notes, edit_note,
    calculate_expression
)

awake_mode = True

# -------------------------
# Response helper
# -------------------------
def respond(gui, message):
    gui.add_message(message, sender="assistant")
    gui.set_state("Speaking")
    asyncio.run(speak(message))
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
                asyncio.run(speak(message))
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

    # Change voice
    if any(t in c for t in ["change voice", "switch voice", "use voice", "set voice", "different voice", "next voice", "male voice", "female voice"]):
        # Helper to apply voice + refresh label thread-safely
        def _apply_voice(vid, label):
            set_voice(vid)
            try:
                gui.refresh_voice_label()
            except AttributeError:
                try:
                    gui.root.after(0, gui._update_voice_label)
                except Exception:
                    pass
            respond(gui, f"Voice changed to {label}.")
            return True

        # Shorthand: "male voice" / "female voice" picks first match in catalog
        if "male voice" in c and "female" not in c:
            for label, vid in VOICE_CATALOG:
                if "male" in label.lower() and "female" not in label.lower():
                    return _apply_voice(vid, label)
        if "female voice" in c:
            for label, vid in VOICE_CATALOG:
                if "female" in label.lower():
                    return _apply_voice(vid, label)
        # "next voice" cycles through the 4-voice catalog
        if "next voice" in c or "different voice" in c:
            current = get_voice()
            ids = [vid for _, vid in VOICE_CATALOG]
            try:
                nxt = ids[(ids.index(current) + 1) % len(ids)]
            except ValueError:
                nxt = ids[0]
            for label, vid in VOICE_CATALOG:
                if vid == nxt:
                    return _apply_voice(vid, label)
        # Try to match a voice name from the catalog (e.g. "change voice to aria")
        for label, vid in VOICE_CATALOG:
            short_label = label.split("(")[0].strip().lower()
            first_name = short_label.split()[0]
            if short_label in c or first_name in c:
                return _apply_voice(vid, label)
        names = ", ".join(l.split(" (")[0] for l, _ in VOICE_CATALOG)
        respond(gui, f"I couldn't find that voice. Say one of: {names}. Or pick from the VOICE menu.")
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

    # Calculator / Unit converter — after identity/purpose so
    # "what is your name" isn't treated as math
    calc_triggers = [
        "calculate", "compute", "solve", "how much is",
        "what is", "what's", "whats", "convert ",
        "plus", "minus", "times", "divided by", "divide by",
        "multiplied by", "multiply", "squared", "cubed",
        "percent", "%",
    ]
    if any(t in c for t in calc_triggers):
        answer = calculate_expression(c)
        if answer is not None:
            respond(gui, answer)
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

    # ---- Notes / Tasks ----
    # Search notes: "search notes for milk" / "find notes milk" / "search note ..."
    if any(t in c for t in ["search notes", "search note", "find notes", "find note"]):
        # extract query after notes/note keyword
        m = re.search(r"(?:search|find)\s+notes?\s*(?:for)?\s*(.*)", c)
        q = m.group(1).strip() if m else ""
        # strip filler words
        for w in ["for ", "about "]:
            if q.startswith(w):
                q = q[len(w):].strip()
        if q:
            respond(gui, search_notes(q))
        else:
            respond(gui, "Tell me what to search — say 'search notes for milk'.")
        return True

    # Clear all notes: "clear notes" / "delete all notes" / "clear all notes"
    if any(t in c for t in ["clear all notes", "delete all notes", "clear notes"]):
        respond(gui, clear_notes())
        return True

    # Edit note: "edit note 2 to new text" / "update note 3 ..."
    edit_match = re.search(r"(?:edit|update)\s+note\s+(\d+)\s+(?:to\s+)?(.+)", c)
    if edit_match:
        try:
            nid = int(edit_match.group(1))
            new_text = edit_match.group(2).strip()
            respond(gui, edit_note(nid, new_text))
        except ValueError:
            respond(gui, "Tell me which note to edit — say 'edit note 2 to buy almond milk'.")
        return True

    # Delete note: "delete note 2" / "remove note milk" / "forget note ..."
    if any(t in c for t in ["delete note", "remove note", "forget note", "delete notes", "remove notes"]):
        m = re.search(r"(?:delete|remove|forget)\s+notes?\s*(.*)", c)
        q = m.group(1).strip() if m else ""
        # strip leading filler
        for w in ["number ", "#", "note "]:
            if q.startswith(w):
                q = q[len(w):].strip()
        respond(gui, delete_note(q))
        return True

    # List notes: "show notes" / "list notes" / "read notes" / "my notes" / "what are my notes"
    if any(t in c for t in ["show notes", "list notes", "read notes", "my notes", "show my notes", "what are my notes"]):
        respond(gui, get_notes())
        return True
    # Also handle bare "notes" when asking to see them
    if c.strip() in ["notes", "show notes"]:
        respond(gui, get_notes())
        return True

    # Add note: "take a note ..." / "add note ..." / "remember that ..." etc.
    note_triggers = [
        "take a note ", "take note ", "add a note ", "add note ",
        "create a note ", "create note ", "remember that ", "remember to ",
        "write down ", "note down ", "save note ",
    ]
    for trig in note_triggers:
        if trig in c:
            content = c.split(trig, 1)[-1].strip()
            # For voice robustness, also try without trailing space trigger
            if content:
                respond(gui, add_note(content))
                return True
    # Fallback trigger without trailing content split — e.g., "note buy milk"
    if c.startswith("note "):
        content = c[5:].strip()
        if content and content not in ["notes"]:
            respond(gui, add_note(content))
            return True

    return False

def handle_typed(command, gui):
    if route_command(command, gui):
        return
    gui.set_state("Thinking")
    reply = brain.think(command)
    respond(gui, reply)

def handle_voice_change(voice_id, gui):
    set_voice(voice_id)
    # Refresh the UI label on the Tk main thread (thread-safe)
    try:
        gui.refresh_voice_label()
    except AttributeError:
        try:
            gui.root.after(0, gui._update_voice_label)
        except Exception:
            pass
    for label, vid in VOICE_CATALOG:
        if vid == voice_id:
            respond(gui, f"Voice changed to {label}.")
            return
    respond(gui, "Voice changed.")

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
    gui.on_voice_change = lambda v: handle_voice_change(v, gui)
    threading.Thread(target=start_dum_e, args=(gui,), daemon=True).start()
    threading.Thread(target=reminder_checker, args=(gui,), daemon=True).start()
    root.mainloop()