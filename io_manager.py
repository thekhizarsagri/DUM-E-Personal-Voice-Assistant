import os
import re
import asyncio
import tempfile
import threading
import speech_recognition as sr
import edge_tts
import pygame

# ----------------------------
# Selected Voice (natural male)
# ----------------------------
selected_voice = "en-US-AndrewNeural"

# Initialize audio mixer once at startup
pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.mixer.init()

# ----------------------------
# TTS (Mouth) — sentence streaming so speech starts fast
# ----------------------------
def _split_sentences(text: str):
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return [p for p in (p.strip() for p in parts) if p]


def _play_file(path: str):
    pygame.mixer.music.load(path)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.wait(30)
    pygame.mixer.music.unload()


async def _synth(path: str, text: str, voice: str):
    await edge_tts.Communicate(text, voice, rate="+4%").save(path)


async def speak(text: str, voice: str = None):
    """Convert text to speech, synthesizing sentence-by-sentence for fast startup."""
    if voice is None:
        voice = selected_voice

    sentences = _split_sentences(text)
    if not sentences:
        return

    tmp = os.path.join(tempfile.gettempdir(), "dum_e_tts")
    os.makedirs(tmp, exist_ok=True)

    # synthesize first sentence (foreground) — this is the "time to first speech"
    first_path = os.path.join(tmp, "0.mp3")
    try:
        await _synth(first_path, sentences[0], voice)
    except Exception as e:
        print(f"TTS error: {e}")
        return

    try:
        # play sentence 0 in a thread while prefetching the next one
        for i, sentence in enumerate(sentences[1:], start=1):
            next_path = os.path.join(tmp, f"{i}.mp3")
            synth_done = threading.Event()

            def _prefetch(p=next_path, s=sentence, v=voice, ev=synth_done):
                try:
                    asyncio.run(_synth(p, s, v))
                except Exception:
                    pass
                finally:
                    ev.set()

            t = threading.Thread(target=_prefetch, daemon=True)
            t.start()
            _play_file(first_path)
            synth_done.wait(timeout=15)
            first_path = next_path

        # play the last sentence
        _play_file(first_path)
    finally:
        try:
            for f in os.listdir(tmp):
                os.remove(os.path.join(tmp, f))
        except OSError:
            pass

# ----------------------------
# Speech Recognition (Ear)
# ----------------------------
_recognizer = sr.Recognizer()
_microphone = sr.Microphone()


async def mic_listener(print_prompt=False, timeout=5, phrase_time_limit=5):
    """Listen from the microphone and return recognized text."""
    try:
        with _microphone as source:
            _recognizer.adjust_for_ambient_noise(source, duration=0.3)
            if print_prompt:
                print("Listening...")
            audio = _recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)

        try:
            command = _recognizer.recognize_google(audio).strip()
            return command if command else None
        except sr.UnknownValueError:
            return None
        except sr.RequestError as e:
            print(f"Speech recognition error: {e}")
            return None
    except sr.WaitTimeoutError:
        return None
    except Exception as e:
        print(f"Microphone error: {e}")
        return None