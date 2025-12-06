# 🌸 Kiku AI Assistant - Project Documentatie

**Versie:** 2.0 (Gemini 2.5 Flash Editie)  
**Auteur:** Martin & Gemini  
**Locatie:** NL

---

## 📖 Introductie
Kiku is een geavanceerde, multimodale AI-assistent die draait op een Raspberry Pi. Ze is ontworpen om te functioneren als een cognitieve ondersteuning en slimme huisgenoot. Ze combineert spraak, visie en planning in één vloeiende interface.

### ✨ Kernfuncties
1.  **🧠 Het Brein:** Aangedreven door **Google Gemini 2.5 Flash**. Razendsnel, context-bewust en spreekt vloeiend Nederlands.
2.  **🗣️ Spraak:** * Luistert continu naar commando's (via Google Speech Recognition).
    * Spreekt terug met een natuurlijke stem.
3.  **👁️ Visie (Dual Mode):**
    * **Kijk-modus:** "Wat zie je?" -> Korte blik in de ruimte.
    * **Scan-modus:** "Scan dit document/object" -> 5 seconden preview op scherm om te richten, daarna gedetailleerde analyse en eventueel vervolgstappen.
4.  **📅 Agenda:** Volledige integratie met **Google Calendar**. Kiku leest je agenda, waarschuwt pro-actief voor afspraken en kan nieuwe items inplannen.
5.  **🖥️ Interface:** Een Sci-Fi GUI op het touchscreen/HDMI scherm met:
    * Een levende, pulserende 3D 'Sphere' (reageert op luisteren/spreken/denken).
    * Live camera-feed (overlay) tijdens het scannen.
    * Geschreven logboek van het gesprek.

---

## 🛠️ Hardware Vereisten

Het systeem is geoptimaliseerd voor de volgende setup:
* **Computer:** Raspberry Pi 4 of 5 (8GB aanbevolen).
* **OS:** Raspberry Pi OS "Trixie" / Bookworm (64-bit).
* **Camera:** Raspberry Pi Camera Module (CSI-interface, via lintkabel). *Geen USB webcam.*
* **Microfoon:** USB Microfoon.
* **Audio:** Luidsprekers (3.5mm jack of USB).
* **Scherm:** HDMI Monitor of Touchscreen.

---

## 🚀 Installatie Handleiding

### 1. Systeemvoorbereiding
Zorg dat je Raspberry Pi up-to-date is en de camera-interface aanstaat.

    sudo apt update && sudo apt upgrade -y
    sudo apt install libcamera-apps python3-venv -y

### 2. Project downloaden

    git clone [https://github.com/martend/kiku.git](https://github.com/martend/kiku.git)
    cd kiku

### 3. Virtuele Omgeving (Venv)
We isoleren de software om conflicten te voorkomen.

    python3 -m venv .venv
    source .venv/bin/activate

### 4. Afhankelijkheden installeren

    pip install -r requirements.txt

*(De `requirements.txt` bevat o.a.: `google-generativeai`, `google-auth`, `SpeechRecognition`, `opencv-python`, `pillow`, `numpy`).*

---

## 🔐 API Configuratie (Cruciaal!)

Kiku heeft toegang nodig tot twee Google diensten. Deze sleutels zijn **geheim** en staan niet op GitHub.

### A. Het AI Brein (Gemini API)
1.  Ga naar [Google AI Studio](https://aistudio.google.com/).
2.  Maak een API Key aan.
3.  Maak een bestand genaamd `.env` in de `kiku` map:
    
    echo "GOOGLE_API_KEY=Jouw_Lange_Sleutel_Hier" > .env

### B. De Agenda (Google Calendar API)
1.  Ga naar de [Google Cloud Console](https://console.cloud.google.com/).
2.  Maak een project aan en schakel de **Google Calendar API** in.
3.  Ga naar 'Credentials' -> 'Create Credentials' -> 'OAuth Client ID' (Type: Desktop App).
4.  Download het JSON-bestand, noem het `credentials.json` en zet het in de `kiku` map.
5.  *Eerste keer starten:* Kiku geeft een URL. Open die op een PC, log in, en plak de code terug (of kopieer de gegenereerde `token.json` naar de Pi).

---

## ▶️ Gebruik

Start Kiku vanuit de terminal (in je venv):

    python3 main.py

### 🗣️ Spraakcommando's

| Categorie | Commando (voorbeeld) | Actie |
| :--- | :--- | :--- |
| **Algemeen** | "Hallo Kiku", "Hoe laat is het?" | Kiku antwoordt. |
| **Visie (Snel)** | "Kiku, wat zie je?", "Kijk eens." | Korte observatie van de omgeving. |
| **Visie (Scan)** | "Scan dit document", "Lees deze baxter." | Live preview (5s) -> Foto -> Analyse. |
| **Agenda** | "Wat staat er in mijn agenda?", "Heb ik afspraken?" | Leest Google Calendar voor. |
| **Beheer** | "Stop", "Ga slapen." | Sluit het programma netjes af. |

---

## 📂 Bestandsstructuur

* `main.py`: Het hart van het systeem. Start de threads (Audio, GUI, Brein, Agenda) en verbindt alles.
* `config.py`: Centrale instellingen (Naam gebruiker, locatie, hardware indexen).
* `modules/`:
    * `brain.py`: Beheert de communicatie met Google Gemini 2.5.
    * `vision.py`: Bestuurt de CSI camera (`rpicam-hello` / `still`).
    * `audio.py`: Spraakherkenning en TTS.
    * `gui.py`: De visuele interface (Tkinter).
    * `calendar_kiku.py`: Koppeling met Google Calendar.
* `.env`: Bevat je API sleutel (Geheim!).
* `token.json`: Bevat je Agenda toegangstoken (Geheim!).

---

## 🚑 Probleemoplossing

* **Zwart beeld bij camera?**
    * Kiku gebruikt de officiële `rpicam` commando's. Controleer of je lintkabel goed zit met `rpicam-hello -t 5000`.
* **Agenda werkt niet?**
    * Verwijder `token.json` en start opnieuw op om opnieuw in te loggen.
* **Microfoon hoort niets?**
    * Check `alsamixer` en zorg dat je 'Capture' volume open staat (F6 om kaart te kiezen).

---
*Documentatie gegenereerd op 06-12-2025*
