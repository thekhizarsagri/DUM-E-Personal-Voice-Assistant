<div align="center">

# 🤖 DUM-E

### ⚡ DEEP UNIVERSAL MIND ELECTRIC ⚡
**Your Cyan-Powered Personal Voice Assistant**

![Python](https://img.shields.io/badge/Python-3.10%2B-00f6ff?style=for-the-badge&logo=python&logoColor=black)
![Groq](https://img.shields.io/badge/Groq-LLM-042e36?style=for-the-badge&logoColor=00f6ff)
![Edge-TTS](https://img.shields.io/badge/Edge--TTS-Voice-00b8c7?style=for-the-badge)
![UI](https://img.shields.io/badge/UI-Cyan_Holo-00f6ff?style=for-the-badge)

*“Sometimes you gotta run before you can walk.”*

</div>

---

## 🌌 What is DUM-E?

Born in **August 2025** just for fun — built on the dream of having your **own JARVIS**.
Talk to it. It listens, thinks, speaks, and acts — wrapped in a glowing **pure-cyan holo interface** with a live arc reactor core.

> 🚀 **Modern Tech Upgrade Incoming** — agentic workflows, real-time audio + deeper skills are on the roadmap.

---

## ✨ Superpowers

| Domain | What it does |
|---|---|
| 🎙️ **Voice In / Out** | Mic input + streaming `edge-tts` speech via `pygame`, 20+ curated voices, in-app VOICE switcher |
| 🧠 **Groq Brain** | Blazing-fast LLM (`openai/gpt-oss-120b` + fallback) with custom persona |
| 🟦 **Cyan Holo UI** | Borderless glass Tkinter HUD — arc reactor, particles, glowing borders, live clock, console |
| 🌦️ **Weather** | Live Open-Meteo data for any city |
| 🌐 **Web & Media** | YouTube play/search, Google search, image lookup |
| 🧮 **Calculator** | Voice math + unit conversion |
| ⏰ **Reminders** | `remind me to ... at ...` with background checker |
| 📝 **Notes & Tasks** | Add / list / search / edit / delete, all by voice |
| 😂 **Jokes** | On-demand laughs |
| 😴 **Sleep / Wake** | Say `sleep dummy` … `hey dummy, wake up` |

---

## 📁 Project Structure

```text
DumE_Project/
├── 🧠 brain.py        # Groq LLM + persona
├── ⚡ dum_e_main.py   # Launcher + intent router
├── 🔊 io_manager.py   # Mic STT + streaming TTS + voices
├── 🛠️ skills.py       # Weather, web, notes, reminders, calc, jokes
├── 🟦 ui.py           # Cyan monochrome holo interface
├── ⚙️ env_config.py   # .env loader
├── 📦 requirements.txt
└── 🔑 .env.example
```

---

## 🚀 Boot It Up

**You need:** Python 3.10+ · Mic + Speakers · Free [Groq API Key](https://console.groq.com)

```bash
# 1. Clone
git clone https://github.com/thekhizarsagri/DUM-E-Personal-Voice-Assistant.git
cd DUM-E-Personal-Voice-Assistant

# 2. Install
pip install -r requirements.txt

# 3. Power the core
cp .env.example .env
# → edit .env: GROQ_API_KEY=gsk_your_key_here

# 4. Wake DUM-E
python dum_e_main.py
```

---

## 🎮 Try Saying

> *“What’s the weather in Mumbai?”*
> *“Calculate 45 times 12 plus 10 percent”*
> *“Remind me to drink water in 20 minutes”*
> *“Take a note buy milk”*
> *“Play Interstellar on YouTube”*
> *“Switch to female voice” / “Next voice”*
> *“Sleep dummy”*

---

<div align="center">

## 👤 Built by **Khizar Sagri**
[![GitHub](https://img.shields.io/badge/GitHub-thekhizarsagri-042e36?style=for-the-badge&logo=github&logoColor=00f6ff)](https://github.com/thekhizarsagri)

**⚡ CORE ONLINE // CYAN STABLE ⚡**

</div>
