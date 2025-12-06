"""
Kiku AI Assistant - Continuous Mode + VISION + GUI
De definitieve integratie.
Versie: Humanized Logs + Geen Dubbele Output.
"""
import sys
import os
import time
import threading
import locale
import re
import config

# --- DISPLAY FIX ---
if os.environ.get('DISPLAY','') == '':
    os.environ.__setitem__('DISPLAY', ':0')

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, PROJECT_ROOT)

from modules.audio import KikuAudio
from modules.brain import KikuBrain
from modules.vision import KikuVision
from modules.gui import KikuUI

STATE = {
    "running": True,
    "mic_active": True
}

ui = None

def clean_text_for_speech(text):
    if not text: return ""
    cleaned = re.sub(r'[^\x00-\x7F\x80-\xFF]', '', text)
    return cleaned.strip()

def get_file_size_mb(path):
    try:
        size = os.path.getsize(path)
        return f"({size / 1024:.1f} KB)"
    except:
        return ""

def input_monitor():
    print("\n[TERMINAL] ENTER = Mic Wissel | 'q' = Stoppen.\n")
    while STATE["running"]:
        try:
            user_input = input()
            if user_input.strip().lower() == 'q':
                stop_kiku()
                break
            STATE["mic_active"] = not STATE["mic_active"]
            status_txt = "Microfoon AAN" if STATE["mic_active"] else "Microfoon UIT"
            print(f"[MENU] {status_txt}")
            if ui: ui.update_status(status_txt)
        except (EOFError, RuntimeError):
            break

def stop_kiku():
    STATE["running"] = False
    print("[SYSTEM] Afsluitprocedure gestart...")
    os._exit(0)

def kiku_backend_logic():
    time.sleep(1)
    
    if ui:
        ui.log("--- Kiku AI: Systemen online ---")
        ui.update_status("Opstarten...")

    try:
        audio = KikuAudio()
        brain = KikuBrain()
        vision = KikuVision()
    except Exception as e:
        err = f"[FATAL] Startfout: {e}"
        print(err)
        if ui: ui.log(err)
        return

    # Introductie
    intro_text = f"Hoi {config.USER_NAME}. Ik ben wakker in {config.RESIDENCE}."
    spoken_intro = clean_text_for_speech(intro_text)
    
    if ui:
        ui.log(f"Kiku > {intro_text}")
        ui.update_status("Klaar")
    
    audio.speak(spoken_intro)

    input_thread = threading.Thread(target=input_monitor, daemon=True)
    input_thread.start()

    errors = 0

    while STATE["running"]:
        try:
            if STATE["mic_active"]:
                if ui: ui.update_status("Luisteren...")
                
                command = audio.listen_continuous()

                if command:
                    errors = 0
                    # LOG: Alleen wat gehoord is
                    if ui: ui.log(f"[Audio] 👂 '{command}'")

                    if "stop" in command or "slapen" in command:
                        audio.speak("Tot later.")
                        stop_kiku()
                        break

                    # Vision
                    image_path = None
                    vision_triggers = ["kijk", "zie", "zien", "wat is dit", "omschrijf", "beschrijf"]

                    if any(trigger in command for trigger in vision_triggers):
                        audio.speak("Momentje...")
                        if ui: ui.log("[Vision] 📷 Foto maken...")
                        image_path = vision.capture_snapshot()
                        if not image_path:
                            audio.speak("Camera fout.")

                    # Context
                    if ui: ui.update_status("Nadenken...")
                    current_time = time.strftime("%H:%M")
                    current_date = time.strftime("%d-%m-%Y")
                    
                    context_command = (
                        f"{command} "
                        f"[Context: Tijd {current_time}, Datum {current_date}, "
                        f"Locatie {config.RESIDENCE}, User {config.USER_NAME}.]"
                    )

                    # Brein
                    response = brain.process_command(context_command, image_path)

                    # LOGGING: Hier voorkomen we dubbele tekst!
                    
                    # 1. Print de leesbare tekst in het scherm
                    if ui: ui.log(f"Kiku > {response}")
                    print(f"Kiku > {response}") 

                    # 2. Spreek het uit (maar print de tekst NIET nog eens)
                    spoken_response = clean_text_for_speech(response)
                    
                    if ui: 
                        # Alleen een icoontje dat audio start
                        ui.update_status("Spreken...")
                    
                    audio.speak(spoken_response)
                    
                    if ui: ui.update_status("Klaar")
                    time.sleep(0.5)
            else:
                if ui: ui.update_status("Microfoon UIT")
                time.sleep(0.5)

        except Exception as e:
            print(f"[FOUT] {e}")
            errors += 1
            if errors > 10:
                time.sleep(2)
                errors = 0

def main():
    global ui
    try:
        ui = KikuUI(on_close_callback=stop_kiku)
    except Exception as e:
        print(f"\n[CRITICAL ERROR] GUI Startfout: {e}")
        sys.exit(1)
    
    backend_thread = threading.Thread(target=kiku_backend_logic, daemon=True)
    backend_thread.start()
    
    try:
        ui.start()
    except KeyboardInterrupt:
        stop_kiku()

if __name__ == "__main__":
    main()
