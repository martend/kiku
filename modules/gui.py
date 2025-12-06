import tkinter as tk
from tkinter import scrolledtext
import sys
import math

class WireframeSphere:
    def __init__(self, canvas, center_x, center_y, radius, color):
        self.canvas = canvas
        self.cx = center_x
        self.cy = center_y
        self.base_radius = radius
        self.radius = radius
        self.color = color
        self.points = []
        self.lines = []
        self.angle_x = 0
        self.angle_y = 0
        self.rotation_speed_x = 0.01
        self.rotation_speed_y = 0.01
        self.pulse_speed = 0.0
        self.pulse_val = 0
        
        self._create_sphere_points()

    def _create_sphere_points(self):
        # Maak punten op een bol (Fibonacci sphere algoritme voor mooie verdeling)
        num_points = 150
        phi = math.pi * (3. - math.sqrt(5.))  # golden angle

        for i in range(num_points):
            y = 1 - (i / float(num_points - 1)) * 2  # y gaat van 1 naar -1
            radius = math.sqrt(1 - y * y)  # radius op y
            theta = phi * i  # golden angle increment

            x = math.cos(theta) * radius
            z = math.sin(theta) * radius
            self.points.append([x, y, z])
        
        # Verbind punten
        for i in range(num_points):
             self.lines.append((i, (i + 1) % num_points))
             self.lines.append((i, (i + 13) % num_points)) # Web structuur

    def set_state(self, state):
        """Past gedrag aan op basis van de status van Kiku."""
        if "Luisteren" in state:
            self.rotation_speed_x = 0.03
            self.rotation_speed_y = 0.02
            self.pulse_speed = 0.08  # Rustig ademen
            self.color = "#00ff00"   # Groen
        elif "Spreken" in state:
            self.rotation_speed_x = 0.05  # Iets sneller draaien
            self.rotation_speed_y = 0.05
            self.pulse_speed = 0.2   # Duidelijke puls, maar geen explosie
            self.color = "#00ccff"   # Blauw
        elif "Nadenken" in state:
            self.rotation_speed_x = 0.08
            self.rotation_speed_y = 0.01
            self.pulse_speed = 0.05
            self.color = "#ffaa00"   # Oranje
        elif "UIT" in state or "Doof" in state:
            self.rotation_speed_x = 0.005 # Heel traag
            self.rotation_speed_y = 0.005
            self.pulse_speed = 0.0
            self.radius = self.base_radius
            self.color = "#333333"   # Grijs
        else:
            # Normaal/Idle
            self.rotation_speed_x = 0.01
            self.rotation_speed_y = 0.01
            self.pulse_speed = 0.05
            self.color = "#00ff00"

    def update(self):
        self.canvas.delete("wireframe")
        
        self.angle_x += self.rotation_speed_x
        self.angle_y += self.rotation_speed_y
        
        # Pulseren (Aangepast: veel subtieler gemaakt)
        if self.pulse_speed > 0:
            self.pulse_val += self.pulse_speed
            # Sinus golf tussen 0.95 en 1.15 (max 15% groter)
            # De multiplier bepaalt de heftigheid
            intensity = 0.15 if self.pulse_speed > 0.1 else 0.05
            scale_factor = 1.0 + (math.sin(self.pulse_val) * intensity)
            self.radius = self.base_radius * scale_factor

        transformed_points = []
        # Rotatie matrices
        cx_rot = math.cos(self.angle_x)
        sx_rot = math.sin(self.angle_x)
        cy_rot = math.cos(self.angle_y)
        sy_rot = math.sin(self.angle_y)

        for x, y, z in self.points:
            # Roteer om X
            y_rot = y * cx_rot - z * sx_rot
            z_rot = y * sx_rot + z * cx_rot
            y = y_rot
            z = z_rot

            # Roteer om Y
            x_rot = x * cy_rot + z * sy_rot
            z_rot = -x * sy_rot + z * cy_rot
            x = x_rot

            # Projecteer
            px = self.cx + x * self.radius
            py = self.cy + y * self.radius
            transformed_points.append((px, py))

        # Teken lijnen
        for p1_idx, p2_idx in self.lines:
            x1, y1 = transformed_points[p1_idx]
            x2, y2 = transformed_points[p2_idx]
            self.canvas.create_line(x1, y1, x2, y2, fill=self.color, width=1, tags="wireframe")

class KikuUI:
    def __init__(self, on_close_callback=None):
        self.on_close_callback = on_close_callback
        
        # Setup Hoofdvenster
        self.root = tk.Tk()
        self.root.title("Kiku AI Interface")
        
        # Fullscreen instellingen
        self.root.attributes('-fullscreen', True)
        self.root.configure(background='black')
        
        # Sluit met ESC toets
        self.root.bind('<Escape>', lambda e: self.on_close())
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        # --- NOODKNOP (RECHTSBOVEN) ---
        self.btn_exit = tk.Button(self.root, text="❌ SLUITEN", 
                                  command=self.on_close,
                                  bg='red', fg='white', font=("Arial", 12, "bold"),
                                  borderwidth=0, activebackground='#ff4444')
        self.btn_exit.place(relx=0.95, rely=0.05, anchor='ne')

        # --- DE VISUELE BOL (HET OOG) ---
        self.canvas = tk.Canvas(self.root, width=400, height=400, bg='black', highlightthickness=0)
        self.canvas.pack(pady=20)
        
        # Maak de 3D bol aan
        self.sphere = WireframeSphere(self.canvas, center_x=200, center_y=200, radius=120, color='#00ff00')

        # --- STATUS TEKST ---
        self.label_status = tk.Label(self.root, text="KIKU ONLINE", 
                                     font=("Courier New", 24, "bold"), 
                                     bg='black', fg='#00ff00')
        self.label_status.pack(pady=10)

        # --- LOG/CHAT VENSTER ---
        self.text_area = scrolledtext.ScrolledText(self.root, 
                                                   font=("Consolas", 14), 
                                                   bg='black', fg='white',
                                                   insertbackground='white',
                                                   borderwidth=0, wrap=tk.WORD)
        self.text_area.pack(padx=50, pady=(0, 50), fill=tk.BOTH, expand=True)

        # Start de animatie loop
        self.animate_sphere()

    def animate_sphere(self):
        """Update de 3D bol."""
        try:
            self.sphere.update()
            # Herhaal elke 30ms
            self.root.after(30, self.animate_sphere)
        except Exception:
            pass

    def update_status(self, text):
        """Update tekst en het gedrag van de bol."""
        self.label_status.config(text=text.upper())
        
        fg_color = "#00ff00"
        if "UIT" in text or "Doof" in text: fg_color = "#555555"
        elif "Luisteren" in text: fg_color = "#00ff00"
        elif "Spreken" in text: fg_color = "#00ccff"
        elif "Nadenken" in text: fg_color = "#ffaa00"
        self.label_status.config(fg=fg_color)

        self.sphere.set_state(text)

    def log(self, text):
        """Schrijf tekst in het grote vak."""
        self.text_area.insert(tk.END, text + "\n\n")
        self.text_area.see(tk.END)

    def start(self):
        self.root.mainloop()

    def on_close(self):
        if self.on_close_callback:
            self.on_close_callback()
        try:
            self.root.destroy()
        except:
            pass
        sys.exit(0)
