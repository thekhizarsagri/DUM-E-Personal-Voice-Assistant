# 🤖 DUM-E: Personal Voice Assistant

> **Deep Universal Mind Electric** — An AI-powered personal voice assistant inspired by Tony Stark's J.A.R.V.I.S.

---

## 📜 Origin Story & About

This project was originally created in **August 2025** just for fun! Driven by the dream of having a personal voice assistant to handle day-to-day tasks like Iron Man's J.A.R.V.I.S., **DUM-E** was built to provide an interactive, voice-driven interface powered by fast AI and dynamic visual feedback.

> 🚀 **Modern Tech Upgrade Coming Soon!**  
> This repository contains the original 2025 codebase of DUM-E uploaded to GitHub. Now, the project is being prepared for a major overhaul to integrate state-of-the-art modern AI tools, agentic workflows, real-time audio models, and expanded skill integrations.

---

## ✨ Features

- 🎙️ **Voice Recognition & Speech Synthesis**: Natural voice input via microphone and instant streaming speech feedback using `edge-tts` and `pygame`.
- 🧠 **Groq LLM Integration**: Fast conversational intelligence powered by Groq's high-speed inference engine (`openai/gpt-oss-120b` with automatic fallback).
- 🎨 **Futuristic Animated UI**: Built with Tkinter featuring glowing neon visual effects, dynamic pulsing orb animations, real-time clock, and custom title bars.
- ⚡ **Voice Skills & Intent Routing**:
  - **Live Weather Data**: Instant local weather updates via Open-Meteo API.
  - **Web & Media Automation**: Quick YouTube search/play, Google search, and Google image lookup.
  - **Time & Date**: Real-time date and time queries.
  - **Identity & Persona**: Custom assistant identity rules, owner recognition, and sleep/wake voice modes ("Sleep Dummy" / "Wake up").

---

## 📁 Project Structure

```text
DumE_Project/
├── brain.py          # Groq LLM integration and system prompt management
├── dum_e_main.py     # Main application launcher and intent routing handler
├── env_config.py     # Environment variable loader (.env configuration)
├── io_manager.py     # Speech-to-Text (STT) and sentence-streaming Text-to-Speech (TTS)
├── skills.py         # Weather, Web Search, YouTube, Image, and Utility skills
├── ui.py             # Custom futuristic Tkinter graphical interface
├── requirements.txt  # Python package dependencies
├── .env.example      # Sample environment file template
└── README.md         # Project documentation
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10 or higher
- Microphone and Speakers connected to your system
- A free [Groq API Key](https://console.groq.com)

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/thekhizarsagri/DUM-E-Personal-Voice-Assistant.git
   cd DUM-E-Personal-Voice-Assistant
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables**:
   Copy `.env.example` to `.env` and insert your Groq API key:
   ```bash
   cp .env.example .env
   ```
   Edit `.env`:
   ```env
   GROQ_API_KEY=gsk_your_actual_groq_api_key_here
   ```

### Running DUM-E

Launch the voice assistant by executing:
```bash
python dum_e_main.py
```

---

## 👤 Author

**Khizar Sagri**  
- GitHub: [@thekhizarsagri](https://github.com/thekhizarsagri)

---

*“Sometimes you gotta run before you can walk.” — Tony Stark*
