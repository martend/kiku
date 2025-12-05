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

# --- 2. HARDWARE NAMEN (NIEUWE FIX: Input naar 'pulse', Output naar 'default') ---
# 'pulse' (Index 8) is de stabielste input voor PyAudio in Trixie/PulseAudio.
MIC_DEVICE_INDEX = 'pulse'
SPEAKER_DEVICE_INDEX = 'default' 

# --- 3. AUDIO INSTELLINGEN ---
CHANNELS = 1
RATE = 48000 
CHUNK = 512 

# Wakeword instellingen
WAKEWORD = "kiku" 

# --- 4. PERSOONLIJKHEID & SYSTEEM ---
SYSTEM_NAME = "Kiku"
AI_NAME = "Kiku"
USER_NAME = "Martin"
RESIDENCE = "Assen"

KIKU_PERSONA = (
    "Je bent Kiku, een geavanceerde, vrouwelijke AI-assistent en metgezel."
    "Je communiceert in het Nederlands met een casual en opgewekte toon."
    "Je hebt langetermijngeheugen en bent ontworpen om de wereld te zien, te interpreteren en te beheren."
    f"Je helpt {USER_NAME} in {RESIDENCE}."
    "Houd rekening met de wens om informatie kort en overzichtelijk te houden vanwege een milde cognitieve beperking."
    "Wees behulpzaam, proactief en lever alleen de gevraagde informatie."
)
