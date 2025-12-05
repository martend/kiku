import pyaudio

def find_audio_devices():
    """
    Toont een lijst van alle beschikbare audio-apparaten met hun indexen.
    Dit script is cruciaal voor het HARD coderen van de IN/OUT indexen.
    """
    audio = pyaudio.PyAudio()
    info = audio.get_host_api_info_by_index(0)
    numdevices = info.get('deviceCount')

    print("\n--- Beschikbare Audio Apparaten (Indexen) ---")
    print("Zoek naar de index van je USB Microfoon (INPUT) en USB Speaker (OUTPUT).")
    print("Plak deze indexen in config.py!\n")

    for i in range(0, numdevices):
        device_info = audio.get_device_info_by_host_api_device_index(0, i)
        
        # We negeren apparaten zonder input of output
        if device_info.get('maxInputChannels') > 0 or device_info.get('maxOutputChannels') > 0:
            
            # Formatteer de apparaatnaam
            name = device_info.get('name')
            
            # Bepaal of het een input, output of beide is
            device_type = ""
            if device_info.get('maxInputChannels') > 0:
                device_type += "INPUT"
            if device_info.get('maxOutputChannels') > 0:
                if device_type: device_type += " / "
                device_type += "OUTPUT"

            print(f"[{i}] {name} ({device_type})")

    print("\n----------------------------------------------\n")
    audio.terminate()

if __name__ == '__main__':
    find_audio_devices()
