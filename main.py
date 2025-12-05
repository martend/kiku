"""
Kiku AI Assistant - Continuous Mode + VISION + MENU
De definitieve integratie van Oren, Mond, Brein en Ogen.
"""
import sys
import os
import time
import threading

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, PROJECT_ROOT)

from modules.audio import KikuAudio
from modules.brain import KikuBrain
from modules.vision import KikuVision

# Globale status voor de threads
STATE = {
    "running": True,
    "mic_active": True
}

def input_monitor():
    """Luistert naar toetsenbord input voor microfoon controle."""
    print("\n---------------------------------------------------")
    print(" ⌨️  BEDIENINGSPANEEL:")
    print("     [ENTER]  -> Wissel Microfoon AAN/UIT")
    print("     'q'      -> Afsluiten")
    print("---------------------------------------------------\n")

    while STATE["running"]:
        try:
            user_input = input()
            if user_input.strip().lower() == 'q':
                print("[MENU] Afsluiten...")
                STATE["running"] = False
                STATE["mic_active"] = False
                break
            
            STATE["mic_active"] = not STATE["mic_active"]
            status_icon = "🟢 AAN" if STATE["mic_active"] else "🔴 UIT (Doof)"
            print(f"\n[MENU] Microfoon is nu: {status_icon}")
        except EOFError:
            break

def main_loop():
    print("--- Kiku AI Assistant: Oren & Ogen Online ---")
    
    try:
        # Initialiseer alle zintuigen
        audio = KikuAudio()
        brain = KikuBrain()
        vision = KikuVision() # De Ogen!
    except Exception as e:
        print(f"[FATAL] Startfout bij initialisatie: {e}")
        return

    intro = f"Hallo Martin. Mijn ogen zijn geactiveerd. Zeg 'Kijk' of 'Wat zie je' om ze te testen."
    audio.speak(intro)

    # Start de toetsenbord monitor
    input_thread = threading.Thread(target=input_monitor, daemon=True)
    input_thread.start()
    
    errors = 0
    
    while STATE["running"]:
        try:
            if STATE["mic_active"]:
                # Luister naar de gebruiker
                command = audio.listen_continuous()
                
                if command:
                    errors = 0 
                    
                    # Stop commando's
                    if "stop" in command or "slapen" in command:
                        audio.speak("Ik ga in stand-by.")
                        # We breken de loop niet helemaal, maar zetten mic uit (optioneel)
                        # Voor nu sluiten we af zoals gevraagd:
                        STATE["running"] = False
                        break
                    
                    # --- VISION TRIGGER LOGICA ---
                    image_path = None
                    # Lijst met triggerwoorden voor de camera
                    vision_triggers = ["kijk", "zie", "zien", "wat is dit", "omschrijf", "beschrijf"]
                    
                    # Check of een van de triggers in het commando zit
                    if any(trigger in command for trigger in vision_triggers):
                        audio.speak("Momentje, ik kijk even...") 
                        # Maak de foto
                        image_path = vision.capture_snapshot()
                        
                        if not image_path:
                            audio.speak("Het lukte niet om mijn camera te gebruiken.")
                    
                    # --- VERWERKING ---
                    # Stuur tekst (en eventueel foto) naar het brein
                    response = brain.process_command(command, image_path)
                    
                    # Spreek het antwoord uit
                    audio.speak(response)
                    
                    # Korte pauze zodat ze zichzelf niet hoort
                    time.sleep(0.5) 
            else:
                # Mic is uit, rustige loop
                time.sleep(0.5)

        except KeyboardInterrupt:
            print("\n[STOP] Geforceerd gestopt.")
            STATE["running"] = False
            break
        except Exception as e:
            print(f"\n[FOUT in Main Loop] {e}")
            errors += 1
            if errors > 10: 
                print("[CRITICAL] Te veel fouten. Pauze...")
                time.sleep(2)
                errors = 0

    print("[SYSTEM] Kiku is afgesloten.")

if __name__ == "__main__":
    main_loop()
