import os
import time
import subprocess

class KikuVision:
    def __init__(self):
        # We kijken welk commando beschikbaar is.
        # Op nieuwe RPi OS is het 'rpicam-', op oudere 'libcamera-'.
        self.cmd_prefix = None
        if self._check_cmd("rpicam-hello"):
            self.cmd_prefix = "rpicam"
        elif self._check_cmd("libcamera-hello"):
            self.cmd_prefix = "libcamera"
        else:
            print("[Vision] ⚠️ GEEN rpicam/libcamera gevonden! Is de camera aangesloten?")

    def _check_cmd(self, cmd):
        from shutil import which
        return which(cmd) is not None

    def start_camera_preview(self, duration=5):
        """
        Toont live beeld direct op het scherm (HDMI overlay).
        Dit blokkeert het script voor 'duration' seconden zodat je kunt richten.
        """
        if not self.cmd_prefix:
            return False
            
        print(f"[Vision] 🎥 Preview starten ({duration}s)...")
        # -t: tijd in ms, -f: fullscreen, -n: geen preview (willen we juist wel!)
        # We gebruiken --nopreview NIET, want we willen zien wat we doen.
        cmd = f"{self.cmd_prefix}-hello -t {duration * 1000} -f"
        
        try:
            # We wachten tot het commando klaar is (dus na 5 seconden)
            subprocess.run(cmd, shell=True, check=True)
            return True
        except Exception as e:
            print(f"[Vision] Fout bij preview: {e}")
            return False

    def capture_snapshot(self):
        """Maakt een foto en slaat deze op."""
        if not self.cmd_prefix:
            return None

        filename = "snapshot.jpg"
        path = os.path.abspath(os.path.join("temp_vision", filename))
        os.makedirs(os.path.dirname(path), exist_ok=True)
        
        print("[Vision] 📸 Foto maken...")
        # -o: output, -t: timeout (kort, want we hebben al gericht), --width/height: resolutie
        # -n: geen preview tijdens foto maken (sneller)
        cmd = f"{self.cmd_prefix}-still -o {path} -t 500 --width 1920 --height 1080 -n"

        try:
            subprocess.run(cmd, shell=True, check=True)
            if os.path.exists(path):
                print(f"[Vision] Succes: {path}")
                return path
        except Exception as e:
            print(f"[Vision] Fout bij foto: {e}")
        
        return None

    # Dummy functies voor compatibiliteit met oude main.py calls
    def start_camera(self): return True
    def stop_camera(self): pass
    def get_frame(self): return None 
    def save_snapshot(self, frame=None): return self.capture_snapshot()
