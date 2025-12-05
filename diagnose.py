import speech_recognition as sr
import pyaudio
import sys
import os

# Importeer config om dezelfde settings te gebruiken
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from config import MIC_DEVICE_INDEX, CHUNK, RATE

def diagnose():
    print("--- AUDIO DIAGNOSE TOOL ---")
    
    # 1. Hardware Check
    p = pyaudio.PyAudio()
    target_index = None
    
    print(f"Zoeken naar apparaat: '{MIC_DEVICE_INDEX}'...")
    
    # Dezelfde logica als in audio.py om te zien wat hij kiest
    if isinstance(MIC_DEVICE_INDEX, str):
        for i in range(p.get_device_count()):
            dev = p.get_device_info_by_index(i)
            if dev.get('name') == MIC_DEVICE_INDEX and dev.get('maxInputChannels') > 0:
                target_index = i
                print(f"-> GEVONDEN: '{dev.get('name')}' op Index {i}")
                break
        
        if target_index is None:
            # Probeer 'pulse' als fallback
            for i in range(p.get_device_count()):
                dev = p.get_device_info_by_index(i)
                if dev.get('name') == 'pulse' and dev.get('maxInputChannels') > 0:
                    target_index = i
                    print(f"-> FALLBACK: 'pulse' gevonden op Index {i}")
                    break
    else:
        target_index = MIC_DEVICE_INDEX
        print(f"-> Directe index gebruikt: {target_index}")

    if target_index is None:
        print("[FATAL] Kan geen invoerapparaat vinden!")
        return

    # 2. Luister Test
    r = sr.Recognizer()
    r.energy_threshold = 300 # Startwaarde
    r.dynamic_energy_threshold = False # We willen ruwe data zien

    try:
        m = sr.Microphone(device_index=target_index, sample_rate=RATE, chunk_size=CHUNK)
        print("\n[TEST 1] Achtergrondruis meten (Wees stil voor 3 seconden...)")
        with m as source:
            r.adjust_for_ambient_noise(source, duration=3)
            print(f"   -> Gemeten Ruisniveau (Threshold): {r.energy_threshold}")
            print(f"   -> (Dit getal moet LAAG zijn, bijv. onder de 300)")

        print("\n[TEST 2] Spraak meten (Zeg hardop 'KIKU TEST'...)")
        with m as source:
            print("   -> Spreek NU!")
            audio = r.listen(source, timeout=5)
            print("   -> Audio ontvangen.")
            
            try:
                # We proberen het te herkennen om te zien of de audio helder is
                tekst = r.recognize_google(audio, language="nl-NL")
                print(f"   -> Google verstond: '{tekst}'")
                print("   -> CONCLUSIE: Audio werkt!")
            except sr.UnknownValueError:
                print("   -> Google kon het niet verstaan (audio te zacht of ruis?)")
            except Exception as e:
                print(f"   -> Fout bij herkenning: {e}")

    except Exception as e:
        print(f"[FATAL] Microfoon kon niet openen: {e}")

if __name__ == "__main__":
    diagnose()
