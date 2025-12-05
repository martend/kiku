# 🤖 Kiku AI Assistant

**Kiku** is een geavanceerde, persoonlijke AI-assistent ontwikkeld in Python. Ze draait lokaal (op bijvoorbeeld een Raspberry Pi), heeft een langetermijngeheugen en kan zowel zien als horen.

## ✨ Kenmerken

* **🧠 Het Brein:** Aangedreven door Google Gemini (Flash 2.0) voor snelle en slimme antwoorden.
* **💾 Langetermijngeheugen:** Kiku onthoudt wie je bent, wat je hebt besproken en specifieke feiten (via een lokale SQLite database).
* **👀 Visie:** Via de camera kan Kiku de wereld om zich heen zien en objecten beschrijven.
* **🗣️ Spraak:** Volledige spraakinteractie (Speech-to-Text & Text-to-Speech).
* **🛡️ Stabiliteit:** Modulair opgebouwd met robuuste foutafhandeling (Hufterproof pad-detectie).

## 📂 Structuur

* `main.py`: Het startpunt van de applicatie.
* `modules/brain.py`: De connectie met de Google Gemini API.
* `modules/memory.py`: Het geheugensysteem (leest/schrijft naar database).
* `modules/vision.py`: Camerabesturing en beeldverwerking.
* `data/`: Hier wordt de lokale database (`kiku.db`) opgeslagen.
* `kluis/`: (Niet op GitHub) Bevat de API-sleutels.

## 🚀 Installatie & Gebruik

1.  **Clone de repository:**
    ```bash
    git clone [https://github.com/martend/kiku.git](https://github.com/martend/kiku.git)
    cd kiku
    ```

2.  **Virtual Environment:**
    ```bash
    python -m venv .venv
    source .venv/bin/activate
    ```

3.  **Configuratie:**
    Plaats je Google Cloud credentials in `kluis/kikukey.json`.

4.  **Start Kiku:**
    ```bash
    python main.py
    ```

## 📝 Auteur
Ontwikkeld door **Martin (Martend)**.
Projectstatus: *Stabiele V1*.

---
*Gegenereerd door Kiku - 2025*
