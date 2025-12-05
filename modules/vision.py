"""
Vision Module (modules/vision.py)
Verantwoordelijk voor het vastleggen en verwerken van beelden.
Gebruikt de moderne libcamera/GStreamer stack voor Raspberry Pi OS "Trixie".
"""
import subprocess
import sys
import os
from pathlib import Path
import time

# --- Import Fix ---
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
# ------------------

# Importeer de configuratie
from config import BASE_DIR

# Map om tijdelijke beelden op te slaan
VISION_DIR = BASE_DIR / "temp_vision"
VISION_DIR.mkdir(exist_ok=True)


class KikuVision:
    """Beheert de Raspberry Pi Camera."""

    def __init__(self):
        print("[Vision] Initialisatie...")
        self.output_path = VISION_DIR / "latest_snapshot.jpg"
        self.is_ready = self._check_libcamera()
        
        if self.is_ready:
            print("[Vision] libcamera/GStreamer lijkt beschikbaar.")
        else:
             print("[Vision] WAARSCHUWING: libcamera-tools niet gevonden. Camerafuncties werken mogelijk niet.")

    def _check_libcamera(self):
        """Controleert of de rpicam-still utility geïnstalleerd is."""
        try:
            subprocess.run(['rpicam-still', '--help'], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True
        except subprocess.CalledProcessError:
             return False
        except FileNotFoundError:
             return False

    def capture_snapshot(self, filename="snapshot.jpg", width=1024, height=768, timeout=2000) -> Path | None:
        """
        Maakt een foto met behulp van de rpicam-still utility (via libcamera).
        """
        output_file = VISION_DIR / filename
        
        command = [
            'rpicam-still',
            '--output', str(output_file),
            '--width', str(width),
            '--height', str(height),
            '--timeout', str(timeout),
            '--nopreview',
        ]
        
        print(f"[Vision] Beeld vastleggen: {output_file.name}...")
        
        try:
            subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            if output_file.exists():
                file_size = output_file.stat().st_size
                # Controleer of het bestand groter is dan 2KB (niet leeg)
                if file_size > 2048:
                    print(f"[Vision] Succes: Beeld opgeslagen: {output_file} ({file_size / 1024:.1f} KB)")
                    return output_file
                else:
                    print(f"[Vision] Fout: Bestand aangemaakt, maar is te klein ({file_size} bytes). Camerafout.")
                    return None
            else:
                print("[Vision] Fout: Commando was succesvol, maar bestand niet gevonden.")
                return None
                
        except subprocess.CalledProcessError as e:
            print(f"[Vision] Fout bij vastleggen (rpicam-still error): {e}")
            return None
        except FileNotFoundError:
             print("[Vision] Fout: 'rpicam-still' niet gevonden. Zorg dat rpicam-apps is geïnstalleerd.")
             return None

if __name__ == '__main__':
    vision_system = KikuVision()
    
    if not vision_system.is_ready:
        print("\nKan niet testen: libcamera-tools niet beschikbaar.")
        exit()
        
    print("\n--- Camera Snapshot Test (Check VISION_DIR) ---")
    
    snapshot_path = vision_system.capture_snapshot(filename="test_kiku_snap.jpg")
    
    if snapshot_path:
        print(f"\nTest succesvol. Controleer het bestand op: {snapshot_path}")
