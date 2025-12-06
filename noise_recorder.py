import pyaudio
import wave
import os
import time

# --- INSTELLINGEN ---
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK = 1024
RECORD_SECONDS = 3  # Korte fragmentjes ruis
OUTPUT_DIR = "training_data/negative" # Hier komt de 'rommel'

def record_noise(num_samples=20):
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f"[INFO] Map aangemaakt: {OUTPUT_DIR}")

    audio = pyaudio.PyAudio()
    
    print(f"\n🔇  KIKU RUIS TRAINER")
    print(f"-----------------------------------")
    print(f"We nemen {num_samples} fragmenten op van je omgeving.")
    print("Maak wat geluid: typen, ademen, rommelen, of stilte.")
    print("Start over 3 seconden...")
    time.sleep(3)

    try:
        for i in range(1, num_samples + 1):
            print(f"[{i}/{num_samples}] Opnemen... ", end="", flush=True)
            
            stream = audio.open(format=FORMAT, channels=CHANNELS,
                                rate=RATE, input=True,
                                frames_per_buffer=CHUNK)
            
            frames = []
            for _ in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
                data = stream.read(CHUNK, exception_on_overflow=False)
                frames.append(data)
            
            print("✅")
            
            stream.stop_stream()
            stream.close()
            
            filename = os.path.join(OUTPUT_DIR, f"noise_{i:03d}.wav")
            wf = wave.open(filename, 'wb')
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(audio.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b''.join(frames))
            wf.close()
            
            # Korte pauze tussen opnames
            time.sleep(0.5)
            
    except KeyboardInterrupt:
        print("\n\n[STOP] Onderbroken.")
    finally:
        audio.terminate()
        print(f"\n🎉 Klaar! Ruis verzameld in {OUTPUT_DIR}")

if __name__ == "__main__":
    record_noise(20)
