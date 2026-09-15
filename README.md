# DUM-E

## Deep Universal Mind Electric

DUM-E is a desktop voice assistant built with Python and Tkinter. It listens through your microphone, uses Groq for natural-language responses, speaks with Edge TTS, and exposes practical tools for weather, web search, media, notes, reminders, and calculations.

## Features

| Area | Capabilities |
| --- | --- |
| Voice | Speech recognition, text-to-speech, and selectable voices |
| Assistant | Groq-powered responses with a custom assistant persona |
| Productivity | Voice notes, note search and editing, and timed reminders |
| Information | Weather lookup, city search, Google search, and image lookup |
| Media | YouTube search and playback |
| Utilities | Natural-language calculations and jokes |
| Controls | Sleep and wake modes, plus a live desktop interface |

## Requirements

- Python 3.10 or newer
- A working microphone and speakers
- A [Groq API key](https://console.groq.com/)
- Internet access for Groq, Edge TTS, weather, and web features

## Installation

From PowerShell or a terminal:

```powershell
git clone https://github.com/thekhizarsagri/DUM-E-Personal-Voice-Assistant.git
cd DUM-E-Personal-Voice-Assistant

python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Create a file named `.env` in the project folder and add your key:

```text
GROQ_API_KEY=gsk_your_key_here
```

Start the assistant:

```powershell
python dum_e_main.py
```

On macOS or Linux, activate the virtual environment with `source .venv/bin/activate` instead.

## Example Commands

Try saying:

- "What is the weather in Mumbai?"
- "Calculate 45 times 12 plus 10 percent"
- "Remind me to drink water in 20 minutes"
- "Take a note: buy milk"
- "Play Interstellar on YouTube"
- "Switch to female voice"
- "Sleep dummy"

## Project Layout

```text
DumE_Project/
├── brain.py          Groq client and assistant persona
├── dum_e_main.py     Application entry point and command routing
├── io_manager.py     Microphone input, speech output, and voices
├── skills.py         Weather, web, media, notes, reminders, and utilities
├── ui.py             Tkinter desktop interface
├── env_config.py     Local .env configuration loader
└── requirements.txt  Python dependencies
```

## Troubleshooting

- If the microphone is not detected, check the system input device and microphone permissions.
- If speech output fails, check that your speakers are available and that the machine is online.
- If the assistant cannot answer, confirm that `.env` is next to `dum_e_main.py` and contains a valid `GROQ_API_KEY`.
- Keep `.env` private. It is intended for local credentials and should not be committed.

## Author

Built by [Khizar Sagri](https://github.com/thekhizarsagri).
