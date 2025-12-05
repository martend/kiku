# Kiku AI Assistant - Project Documentatie

## 👩‍💻 Over Kiku
Kiku is een geavanceerde, modulaire, open-source AI-assistent / gezelschapsrobot, gebouwd rond een **Raspberry Pi 4**. Het doel is het creëren van een Jarvis-achtige entiteit met **persoonlijkheid**, **langetermijngeheugen** en **visuele intelligentie**.

Het project wordt ontwikkeld met nadruk op **kwaliteit, betrouwbaarheid en strikte modulariteit** (Python 3.11+, Raspberry Pi OS "Trixie").

## 🛠️ Architectuur & Technologie Stack
* **Besturingssysteem:** Raspberry Pi OS "Trixie" (64-bit)
* **Hardware:** Raspberry Pi 4 (4GB+), NVMe SSD, USB Audio (Mic/Speaker), Raspberry Pi Camera Module.
* **Basis Taal:** Python 3 (met gevirtualiseerde omgeving: `venv`).
* **Audio:** PulseAudio & ALSA (Hardware-Indexen worden HARD gecodeerd in `config.py`).
* **Vision:** libcamera-stack & GStreamer.
* **Conversatie:** Natural Language Processing (via Google Gemini API).

## 🗂️️ Modulaire Structuur
| Bestand | Rol |
| :--- | :--- |
| `main.py` | De **App-Entrypoint**. Initialiseert modules en beheert de hoofdloop. |
| `config.py` | Centrale configuratie. Bevat **HARDWARE-INDEXEN**, API-sleutels, etc. |
| `modules/audio.py` | Beheert STT/TTS (Spraakherkenning en -synthese) en hardware-validatie. |
| `modules/vision.py` | Beheert Camera, Objectherkenning en Visuele Analyse. |
| `modules/brain.py` | De **AI Kern**. Beheert langetermijngeheugen en conversatie. |
| `modules/tools.py` | Functionele tools (Calendar, Sys-Monitor, News, DJ Modus). |
| `modules/interface.py` | Beheert de visuele output (Sci-Fi HUD / 3D Model). |
