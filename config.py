"""
Centrale configuratie voor Kiku AI Assistant.
"""

import os
from pathlib import Path

# --- 1. PROJECT PADEN ---
BASE_DIR = Path(__file__).resolve().parent
LOG_DIR = BASE_DIR / "logs"
TEMP_AUDIO_DIR = BASE_DIR / "temp_audio"
TEMP_AUDIO_DIR.mkdir(exist_ok=True)

# --- 2. HARDWARE ---
MIC_DEVICE_INDEX = 'pulse'
SPEAKER_DEVICE_INDEX = 'default'

# --- 3. AUDIO INSTELLINGEN ---
CHANNELS = 1
RATE = 48000
CHUNK = 512

# --- 4. PERSOONLIJKHEID & SYSTEEM ---
SYSTEM_NAME = "Kiku"
AI_NAME = "Kiku"
USER_NAME = "Martin"
RESIDENCE = "Assen"

# Hier zit de 'magie' van haar gedrag
KIKU_PERSONA = (
    f"Je bent {AI_NAME}, de slimme assistent van {USER_NAME} in {RESIDENCE}."
    "ANTWOORD STIJL:"
    "- Houd antwoorden kort, direct en casual."
    "- Noem de gebruiker NIET bij elke zin bij naam (alleen bij begroeting)."
    "- Zeg NIET steeds wie jij bent."
    "- Als je een tijd noemt, kies één formaat (bijv. '23:00 uur') en noem het niet dubbel."
    "- Gebruik emojis spaarzaam."
    "- Je hebt toegang tot een geheugen, gebruik dat voor context."
)
