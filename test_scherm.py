import tkinter as tk
import os

# Zorg dat het op het scherm van de Pi verschijnt
os.environ["DISPLAY"] = ":0"

def sluit_af(event=None):
    root.destroy()

# Het hoofdvenster maken
root = tk.Tk()
root.title("Kiku Display")

# Volledig scherm en zwart
root.attributes('-fullscreen', True)
root.configure(bg='black')

# Tekst toevoegen
label = tk.Label(
    root, 
    text="Hallo Martin!\nIk ben Kiku.\n\nLocatie: Assen\nStatus: Online", 
    font=("Courier", 40, "bold"), 
    fg="#00ff00",  # Hacker groen
    bg="black"
)
label.pack(expand=True)

# Instructie om af te sluiten
hint = tk.Label(root, text="Druk op ESC om te sluiten", fg="gray", bg="black")
hint.pack(side="bottom", pady=20)

# ESC toets koppelen aan afsluiten
root.bind('<Escape>', sluit_af)

# Start de loop
root.mainloop()
