"""
Audio Module (modules/audio.py)
Verantwoordelijk voor Spraakherkenning (STT) en Spraaksynthese (TTS).
Bevat 'Nuclear Option' voor error suppression en geforceerde PulseAudio output.
"""
import time
import subprocess
import os
import sys
import re
import speech_recognition as sr
from gtts import gTTS
import pyaudio 
from ctypes import *
from contextlib import contextmanager

# --- IMPORT FIX ---
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from config import RATE, CHUNK

# --- DE 'NUCLEAR OPTION' TEGEN LOG SPAM ---
# Deze functie leidt stderr (foutmeldingen) tijdelijk om naar /dev/null
# Dit is de enige manier om die hardnekkige JACK/ALSA meldingen te stoppen.
@contextmanager
def ignore_stderr():
    try:
        devnull = os.open(os.devnull, os.O_WRONLY)
        old_stderr = os.dup(2)
        sys.stderr.flush()
        os.dup2(devnull, 2)
        os.close(devnull)
        try:
            yield
        finally:
            os.dup2(old_stderr, 2)
            os.close(old_stderr)
    except Exception:
        # Als dit faalt (bijv. op Windows), doe dan niets en laat logs gewoon zien
        yield

# C-Level ALSA handler (dubbele beveiliging)
ERROR_HANDLER_FUNC = CFUNCTYPE(None, c_char_p, c_int, c_char_p, c_int, c_char_p)
def py_error_handler(filename, line, function, err, fmt):
    pass
c_error_handler = ERROR_HANDLER_FUNC(py_error_handler)
try:
    asound = cdll.LoadLibrary('libasound.so.2')
    asound.snd_lib_error_set_handler(c_error_handler)
except:
    pass
# ------------------------------------------

class KikuAudio:
    def __init__(self):
        # We gebruiken de 'ignore_stderr' wrapper om PyAudio stil te houden tijdens start
        with ignore_stderr():
            self.recognizer = sr.Recognizer()
            self.recognizer.energy_threshold = 3000
            self.recognizer.dynamic_energy_threshold = False
            self.recognizer.pause_threshold = 0.8
            
            # Initialiseer PyAudio eenmalig om te checken of het werkt
            self.p = pyaudio.PyAudio()
        
        print(f"[Audio] Systeem Gereed (Logs onderdrukt). Drempel: 3000")
        
        self.is_listening = False
        from config import TEMP_AUDIO_DIR
        self.TEMP_AUDIO_DIR = TEMP_AUDIO_DIR
        self.TEMP_AUDIO_DIR.mkdir(exist_ok=True)

    def clean_text_for_tts(self, text):
        """Maakt tekst schoon (geen emojis, geen markdown)."""
        if not text: return ""
        text = text.replace("*", "").replace("#", "").replace("_", "")
        emoji_pattern = re.compile("["
            u"\U0001F600-\U0001F64F"
            u"\U0001F300-\U0001F5FF"
            u"\U0001F680-\U0001F6FF"
            u"\U0001F1E0-\U0001F1FF"
            "]+", flags=re.UNICODE)
        return emoji_pattern.sub(r'', text)

    def speak(self, text, wait_for_completion=True):
        if not text: return
        
        print(f"[Kiku] 🗣️ {text}")
        clean_text = self.clean_text_for_tts(text)

        try:
            tts = gTTS(text=clean_text, lang='nl')
            tts_path = self.TEMP_AUDIO_DIR / "tts_output.mp3"
            tts.save(str(tts_path))

            # --- MPV COMMANDO UPDATE ---
            # We voegen '--ao=pulse' toe. Dit dwingt MPV om PulseAudio te gebruiken
            # en niet te zoeken naar JACK, wat de stilte zou moeten oplossen.
            playback_command = [
                'mpv', 
                '--no-terminal', 
                '--ao=pulse', 
                '--volume=100', 
                str(tts_path)
            ]
            
            # We sturen de output van MPV ook naar DEVNULL om de terminal schoon te houden
            process = subprocess.Popen(playback_command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            if wait_for_completion:
                process.wait()
            os.remove(tts_path)
        except Exception as e:
            print(f"[ERROR] TTS Fout: {e}")

    def listen_continuous(self):
        """Luistert één keer naar een zin."""
        try:
            # Ook hier onderdrukken we de logs tijdens het openen van de microfoon
            with ignore_stderr():
                mic = sr.Microphone(sample_rate=RATE, chunk_size=CHUNK)
                
                with mic as source:
                    print(".", end="", flush=True) 
                    try:
                        audio_data = self.recognizer.listen(source, timeout=3, phrase_time_limit=10)
                    except sr.WaitTimeoutError:
                        return None 

            # Verwerking mag weer logs tonen (print statements)
            print("\n[Audio] 🎤 Verwerken...")
            text = self.recognizer.recognize_google(audio_data, language="nl-NL")
            print(f"[Audio] 👂 Gehoord: '{text}'")
            return text.lower()

        except sr.UnknownValueError:
            return None 
        except Exception as e:
            # print(f"\n[Audio] Fout: {e}") # Uitgezet voor rust
            return None
