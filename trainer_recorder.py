import pyaudio
import wave
import os
import time

# --- INSTELLINGEN ---
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000  # Belangrijk: openWakeWord werkt het best op 16kHz
CHUNK = 1024
RECORD_SECONDS = 2.5  # Iets langer dan het woord, om afkappen te voorkomen
OUTPUT_DIR = "training_data/positive" # Hier komen je stemmen
WAKE_WORD = "kiku"

def record_samples(num_samples=50):
    # Maak de map als die nog niet bestaat
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f"[INFO] Map aangemaakt: {OUTPUT_DIR}")

    audio = pyaudio.PyAudio()

    # Zoek standaard input device
    # We laten PyAudio zelf kiezen (meestal 'default'), dat werkt vaak het best voor opnames
    
    print(f"\n🎙️  WELKOM BIJ DE KIKU STEM TRAINER")
    print(f"-----------------------------------")
    print(f"We gaan {num_samples} opnames maken van het woord '{WAKE_WORD}'.")
    print(f"De bestanden worden opgeslagen in: {OUTPUT_DIR}")
    print("Druk op CTRL+C om eerder te stoppen.\n")

    start_index = len(os.listdir(OUTPUT_DIR)) + 1
    
    try:
        for i in range(start_index, start_index + num_samples):
            input(f"[{i}/{start_index + num_samples - 1}] Druk op ENTER en zeg '{WAKE_WORD}'...")
            
            print("🔴 Opnemen...", end="", flush=True)
            
            stream = audio.open(format=FORMAT, channels=CHANNELS,
                                rate=RATE, input=True,
                                frames_per_buffer=CHUNK)
            
            frames = []
            for _ in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
                data = stream.read(CHUNK, exception_on_overflow=False)
                frames.append(data)
            
            print(" ✅ Klaar.")
            
            stream.stop_stream()
            stream.close()
            
            # Opslaan
            filename = os.path.join(OUTPUT_DIR, f"{WAKE_WORD}_{i:03d}.wav")
            wf = wave.open(filename, 'wb')
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(audio.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b''.join(frames))
            wf.close()
            
    except KeyboardInterrupt:
        print("\n\n[STOP] Training onderbroken. Geen probleem!")
    finally:
        audio.terminate()
        print(f"\n🎉 Klaar! Je hebt {len(os.listdir(OUTPUT_DIR))} samples verzameld.")

if __name__ == "__main__":
    record_samples(50)
