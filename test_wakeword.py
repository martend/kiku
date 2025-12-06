import pyaudio
import numpy as np
import pickle
import openwakeword
from openwakeword.model import Model
import os
import ctypes
import sys
from contextlib import contextmanager

# --- INSTELLINGEN ---
MODEL_FILE = "kiku_model.pkl"
CHANNELS = 1
RATE = 16000
CHUNK = 1280
MIC_INDEX = 4    # PulseAudio

# --- ERROR SUPPRESSOR ---
ERROR_HANDLER_FUNC = ctypes.CFUNCTYPE(None, ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p)
def py_error_handler(filename, line, function, err, fmt):
    pass
c_error_handler = ERROR_HANDLER_FUNC(py_error_handler)

@contextmanager
def no_alsa_err():
    try:
        asound = ctypes.cdll.LoadLibrary('libasound.so')
        asound.snd_lib_error_set_handler(c_error_handler)
        yield
        asound.snd_lib_error_set_handler(None)
    except:
        yield

def main():
    print(f"--- KIKU MATRIX DEBUG ---")
    
    if not os.path.exists(MODEL_FILE):
        print(f"❌ FOUT: Kan {MODEL_FILE} niet vinden.")
        return
        
    print(f"Loading {MODEL_FILE}...")
    with open(MODEL_FILE, 'rb') as f:
        kiku_brain = pickle.load(f)

    print("Loading Engine...")
    with no_alsa_err():
        try:
            oww_model = Model(inference_framework="onnx")
        except:
            oww_model = Model()

    print("✅ Alles geladen.")
    print("---------------------------------------")
    print(f"🎤 Mic {MIC_INDEX} (PulseAudio) open...")
    print("Praat nu tegen Kiku. Je moet de balkjes zien bewegen!")
    print("---------------------------------------")

    audio = pyaudio.PyAudio()
    
    try:
        stream = audio.open(format=pyaudio.paInt16,
                            channels=CHANNELS,
                            rate=RATE,
                            input=True,
                            frames_per_buffer=CHUNK,
                            input_device_index=MIC_INDEX)
    except Exception as e:
        print(f"\n❌ PulseAudio Error: {e}")
        return

    try:
        print("\n   VOLUME   |  SCORE  | STATUS")
        print("------------+---------+-------")
        while True:
            data = stream.read(CHUNK, exception_on_overflow=False)
            audio_data = np.frombuffer(data, dtype=np.int16)

            # 1. Bereken Volume
            volume = np.abs(audio_data).mean()
            vol_bars = "#" * int(volume / 50) 
            if len(vol_bars) > 10: vol_bars = vol_bars[:10]
            vol_display = f"{vol_bars:<10}" # Zorg dat het altijd 10 tekens breed is

            # 2. Voorspel
            oww_model.predict(audio_data)

            score = 0.0
            emb = None
            if hasattr(oww_model, 'last_embeddings') and oww_model.last_embeddings is not None:
                emb = oww_model.last_embeddings
            
            if emb is not None:
                prediction = kiku_brain.predict_proba(emb.reshape(1, -1))
                score = prediction[0][1]

            # 3. Toon resultaat (gebruik \r om op dezelfde regel te blijven)
            status = ""
            if score > 0.5: status = "🚀 KIKU!"
            elif score > 0.2: status = "🤔 Hmmm?"
            
            # Alleen printen als er geluid is OF de score interessant is
            # (Anders flikkert het scherm te veel)
            if volume > 100 or score > 0.01:
                print(f"\r   {vol_display} |  {score:.3f}  | {status}", end="", flush=True)
                
            if score > 0.5:
                # Als we een hit hebben, printen we even een nieuwe regel zodat hij blijft staan
                print("") 

    except KeyboardInterrupt:
        print("\n\n👋 Gestopt.")
    finally:
        try:
            stream.stop_stream()
            stream.close()
            audio.terminate()
        except:
            pass

if __name__ == "__main__":
    main()
