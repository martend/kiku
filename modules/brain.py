"""
Kiku Brain Module (modules/brain.py)
Geïntegreerd met SQLite Geheugen (modules/memory.py).
"""
import sys
import os
from pathlib import Path
try:
    from PIL import Image
except ImportError:
    Image = None

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from config import KIKU_PERSONA, USER_NAME
from kluis.keys import GEMINI_API_KEY 
from modules.memory import KikuMemory # Importeer het geheugen
from google import genai
from google.genai import types

class KikuBrain:
    def __init__(self):
        print("[Brain] Initialisatie...")
        self.USER_NAME = USER_NAME 
        self.memory = KikuMemory() # Start de geheugen module

        if not GEMINI_API_KEY:
            print("[CRITICAL] Geen API Key!")
            self.chat = None
            return

        try:
            self.client = genai.Client(api_key=GEMINI_API_KEY)
            
            # Laad de geschiedenis uit de database!
            history = self.memory.get_recent_context(limit=20) # Haal de laatste 20 interacties
            
            config = types.GenerateContentConfig(
                system_instruction=KIKU_PERSONA
            )

            # Start sessie MET geschiedenis
            self.chat = self.client.chats.create(
                model='gemini-2.5-flash', 
                config=config,
                history=history # Injecteer het langetermijngeheugen
            )
            print(f"[Brain] Kiku Online. Geheugen geladen ({len(history)} berichten).")
            
        except Exception as e:
            print(f"[ERROR] Brain startfout: {e}")
            self.chat = None

    def process_command(self, command: str, image_path: Path = None) -> str:
        if not self.chat:
            return "Mijn brein functioneert niet."

        print(f"[Brain] 🤔 Verwerkt: '{command}'")
        
        # 1. Sla de vraag van de gebruiker op in het geheugen
        self.memory.add_message("user", command, image_path)
        
        try:
            response_obj = None
            
            # Verstuur naar Gemini (Google onthoudt dit sessie-technisch ook, maar wij slaan het op voor herstarts)
            if image_path and Image:
                print(f"[Brain] 👁️ + Tekst")
                try:
                    img = Image.open(image_path)
                    response_obj = self.chat.send_message([command, img])
                except Exception as img_err:
                    print(f"[Brain] Afbeelding fout: {img_err}")
                    response_obj = self.chat.send_message(command)
            else:
                response_obj = self.chat.send_message(command)
            
            response_text = response_obj.text
            
            # 2. Sla het antwoord van Kiku op in het geheugen
            self.memory.add_message("model", response_text)
            
            return response_text
            
        except Exception as e:
            print(f"[ERROR] Gemini Fout: {e}")
            return "Ik ben de draad even kwijt."
