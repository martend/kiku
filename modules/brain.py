import google.generativeai as genai
import os
from dotenv import load_dotenv

# 1. Laad de geheime sleutels uit .env
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("[Brain] ❌ CRITISCHE FOUT: Geen GOOGLE_API_KEY gevonden in .env bestand!")

# 2. Configureer Gemini
try:
    genai.configure(api_key=api_key)
except Exception as e:
    print(f"[Brain] Configuratie fout: {e}")

# Instellingen voor het model
generation_config = {
    "temperature": 0.7,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 1024,
}

# De systeem-instructie (Karakter)
SYSTEM_PROMPT = """
Je bent Kiku, een vrolijke, behulpzame AI-assistent in Assen.
Je spreekt Nederlands. Houd je antwoorden kort, bondig en casual.
Gebruik geen opmaak zoals '**' in je spraak, maar wel in tekst.

Je krijgt vaak context mee tussen haakjes [...].
Gebruik die informatie (zoals agenda, tijd, wat je ziet) om slim te antwoorden.
Als er in de agenda-context staat 'Afspraak met X', meld dat dan duidelijk.
"""

class KikuBrain:
    def __init__(self):
        print("[Brain] Initialisatie...")
        try:
            # UPGRADE: We pakken de nieuwste 2.5 Flash!
            self.model = genai.GenerativeModel(
                model_name="gemini-2.5-flash",
                generation_config=generation_config,
                system_instruction=SYSTEM_PROMPT
            )
            self.chat = self.model.start_chat(history=[])
            print("[Brain] Kiku Online (Model: Gemini 2.5 Flash).")
        except Exception as e:
            print(f"[Brain] ❌ Startfout: {e}")

    def process_command(self, text_input, image_path=None):
        """Verwerkt tekst en (optioneel) een plaatje."""
        try:
            print(f"[Brain] 🤔 Verwerkt: '{text_input}'")
            
            # 1. Alleen Tekst
            if not image_path:
                response = self.chat.send_message(text_input)
                return response.text

            # 2. Tekst + Beeld (Vision)
            else:
                print("[Brain] 👁️ + Tekst verwerking...")
                if os.path.exists(image_path):
                    # Upload plaatje naar Gemini
                    img_file = genai.upload_file(image_path)
                    
                    # Wachten op verwerking (Gemini heeft soms een seconde nodig)
                    import time
                    while img_file.state.name == "PROCESSING":
                        time.sleep(0.5)
                        img_file = genai.get_file(img_file.name)

                    if img_file.state.name == "FAILED":
                        return "Het verwerken van de foto is mislukt."

                    # Stuur plaatje + tekst
                    response = self.chat.send_message([text_input, img_file])
                    return response.text
                else:
                    return "Ik probeerde te kijken, maar de foto is mislukt."

        except Exception as e:
            print(f"[ERROR] Gemini Fout: {e}")
            return "Ik ben de draad even kwijt (Fout in mijn hoofd)."
