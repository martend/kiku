import sys
import os
import time
import threading
import config

if os.environ.get('DISPLAY','') == '':
    os.environ.__setitem__('DISPLAY', ':0')

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, PROJECT_ROOT)

from modules.audio import KikuAudio
from modules.brain import KikuBrain
from modules.vision import KikuVision
from modules.gui import KikuUI
from modules.calendar_kiku import KikuCalendar

STATE = {"running": True, "mic_active": True}
ui = None
calendar = None

def clean_text_for_speech(text):
    if not text: return ""
    import re
    cleaned = re.sub(r'[^\x00-\x7F\x80-\xFF]', '', text)
    return cleaned.strip()

def input_monitor():
    while STATE["running"]:
        try:
            user_input = input()
            if user_input.strip().lower() == 'q':
                stop_kiku()
                break
            STATE["mic_active"] = not STATE["mic_active"]
            status_txt = "Microfoon AAN" if STATE["mic_active"] else "Microfoon UIT"
            if ui: ui.update_status(status_txt)
        except:
            break

def stop_kiku():
    STATE["running"] = False
    print("[SYSTEM] Afsluiten...")
    os._exit(0)

def calendar_watcher(audio_module):
    while STATE["running"]:
        if calendar:
            try:
                reminders = calendar.check_upcoming_reminders()
                for msg in reminders:
                    if ui: ui.log(f"[Agenda] 🔔 {msg}")
                    audio_module.speak(msg)
                    time.sleep(5)
            except:
                pass
        time.sleep(60)

def kiku_backend_logic():
    global calendar
    time.sleep(1)
    if ui: ui.log("--- Kiku AI: Systeem Start (Dual Vision Mode) ---")

    try:
        audio = KikuAudio()
        brain = KikuBrain()
        vision = KikuVision()
        try:
            calendar = KikuCalendar()
            if ui: ui.log("✅ Agenda verbonden!")
        except Exception as e:
            if ui: ui.log(f"⚠️ Agenda werkt niet: {e}")
    except Exception as e:
        if ui: ui.log(f"[FATAL] {e}")
        return

    if calendar:
        threading.Thread(target=calendar_watcher, args=(audio,), daemon=True).start()

    intro_text = f"Hoi {config.USER_NAME}. Ik ben er klaar voor."
    if ui:
        ui.log(f"Kiku > {intro_text}")
        ui.update_status("Klaar")
    audio.speak(intro_text)

    threading.Thread(target=input_monitor, daemon=True).start()

    while STATE["running"]:
        try:
            if STATE["mic_active"]:
                if ui: ui.update_status("Luisteren...")
                command = audio.listen_continuous()

                if command:
                    # --- VISION LOGICA (GESPLITST) ---
                    image_path = None
                    vision_mode = None # 'general' of 'document'
                    
                    # Lijsten met triggerwoorden
                    triggers_doc = ["scan", "lees", "document", "baxter", "medicijn", "brief", "tekst"]
                    triggers_general = ["kijk", "zie", "zien", "wat is dit", "omschrijf", "beschrijf"]

                    # 1. Check eerst op DOCUMENT SCAN (Specifieker)
                    if any(word in command for word in triggers_doc):
                        vision_mode = "document"
                        audio.speak("Oké, document scannen. Houd het 5 seconden stil voor de camera.")
                        preview_time = 5
                        
                    # 2. Check anders op ALGEMENE BLIK
                    elif any(word in command for word in triggers_general):
                        vision_mode = "general"
                        audio.speak("Ik kijk even mee...")
                        preview_time = 2

                    # Als we gaan kijken (in welke modus dan ook):
                    if vision_mode:
                        if ui: 
                            ui.update_status(f"Camera ({vision_mode})...")
                            ui.log(f"[Vision] 🎥 Start preview ({preview_time}s)...")
                        
                        # Start Preview (Overlay)
                        vision.start_camera_preview(duration=preview_time)
                        
                        # Maak Foto
                        audio.speak("Klik!")
                        image_path = vision.capture_snapshot()
                        
                        if not image_path:
                            audio.speak("Mijn camera liet me in de steek.")
                            vision_mode = None # Abort

                    # --- CONTEXT & PROMPT BOUWEN ---
                    if ui: ui.update_status("Nadenken...")
                    current_time = time.strftime("%H:%M")
                    
                    agenda_text = ""
                    if calendar:
                        events = calendar.get_week_preview()
                        if events:
                            agenda_text = "Agenda: " + ", ".join([f"{e['summary']} op {e['start'].get('dateTime', e['start'].get('date'))}" for e in events[:3]])

                    # Basis Context
                    system_context = f"Systeem: Tijd {current_time}. {agenda_text}. Locatie {config.RESIDENCE}."

                    # Specifieke instructies toevoegen op basis van modus
                    if vision_mode == "document":
                        system_context += " [SCAN MODUS: De gebruiker toont een document (zoals een medicijnzakje/baxter of brief). Lees ALLE tekst, datums en tijden nauwkeurig. Vat samen wat er moet gebeuren.]"
                    elif vision_mode == "general":
                        system_context += " [KIJK MODUS: Beschrijf kort wat je ziet in de ruimte of wat de gebruiker vasthoudt.]"

                    full_command = f"{command} [{system_context}]"

                    response = brain.process_command(full_command, image_path)

                    if ui: ui.log(f"Kiku > {response}")
                    print(f"Kiku > {response}") 

                    spoken_response = clean_text_for_speech(response)
                    if ui: ui.update_status("Spreken...")
                    audio.speak(spoken_response)
                    
                    if ui: ui.update_status("Klaar")
                    time.sleep(0.5)
            else:
                if ui: ui.update_status("Microfoon UIT")
                time.sleep(0.5)

        except Exception as e:
            print(f"[FOUT] {e}")

def main():
    global ui
    try:
        ui = KikuUI(on_close_callback=stop_kiku)
    except:
        sys.exit(1)
    
    threading.Thread(target=kiku_backend_logic, daemon=True).start()
    
    try:
        ui.start()
    except KeyboardInterrupt:
        stop_kiku()

if __name__ == "__main__":
    main()
