"""
Memory Module (modules/memory.py)
Beheert het langetermijngeheugen via SQLite.
Slaat gesprekken en feiten op in kiku/data/kiku.db.
"""
import sqlite3
import time
import os
from pathlib import Path

# --- HUFTERPROOF PAD LOCATIE ---
CURRENT_DIR = Path(__file__).parent.absolute()
PROJECT_ROOT = CURRENT_DIR.parent
DATA_DIR = PROJECT_ROOT / "data"
DB_PATH = DATA_DIR / "kiku.db"

class KikuMemory:
    def __init__(self):
        self.db_path = DB_PATH
        
        if not DATA_DIR.exists():
            DATA_DIR.mkdir(parents=True, exist_ok=True)
            
        self._init_db()
        print(f"[Memory] Database verbonden: {self.db_path}")

    def _init_db(self):
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute('''CREATE TABLE IF NOT EXISTS conversation_history
                         (id INTEGER PRIMARY KEY AUTOINCREMENT,
                          timestamp REAL,
                          role TEXT,
                          content TEXT,
                          image_path TEXT)''')
            c.execute('''CREATE TABLE IF NOT EXISTS facts
                         (key TEXT PRIMARY KEY,
                          value TEXT,
                          timestamp REAL)''')
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"[Memory] CRITICAL ERROR bij init_db: {e}")

    def add_message(self, role, content, image_path=None):
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            img_str = str(image_path) if image_path else None
            c.execute("INSERT INTO conversation_history (timestamp, role, content, image_path) VALUES (?, ?, ?, ?)",
                      (time.time(), role, content, img_str))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"[Memory] Fout bij opslaan bericht: {e}")

    def get_recent_context(self, limit=10):
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row 
            c = conn.cursor()

            c.execute("SELECT role, content FROM conversation_history ORDER BY id DESC LIMIT ?", (limit,))
            rows = c.fetchall()
            conn.close()

            history = []
            for row in reversed(rows):
                role = "user" if row['role'] == "user" else "model"
                
                # --- DE FIX ZIT HIER ---
                # Google wil dat 'parts' een lijst met objecten is, niet platte tekst.
                # We maken er nu {"text": "..."} van.
                history.append({
                    "role": role, 
                    "parts": [{"text": row['content']}]
                })

            return history
        except Exception as e:
            print(f"[Memory] Fout bij ophalen context: {e}")
            return []

    def clear_history(self):
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute("DELETE FROM conversation_history")
            conn.commit()
            conn.close()
            print("[Memory] Geheugen gewist.")
        except Exception as e:
            print(f"[Memory] Fout bij wissen: {e}")

if __name__ == "__main__":
    print(f"Test Mode. Pad naar DB is: {DB_PATH}")
    mem = KikuMemory()
    context = mem.get_recent_context(limit=2)
    print(f"Test context opgehaald: {context}")
