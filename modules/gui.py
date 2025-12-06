import tkinter as tk
from tkinter import scrolledtext
import sys
import math
import cv2
from PIL import Image, ImageTk # Nodig voor plaatjes in GUI

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
        num_points = 150
        phi = math.pi * (3. - math.sqrt(5.))
        for i in range(num_points):
            y = 1 - (i / float(num_points - 1)) * 2
            radius = math.sqrt(1 - y * y)
            theta = phi * i
            x = math.cos(theta) * radius
            z = math.sin(theta) * radius
            self.points.append([x, y, z])
        for i in range(num_points):
             self.lines.append((i, (i + 1) % num_points))
             self.lines.append((i, (i + 13) % num_points))

    def set_state(self, state):
        if "Luisteren" in state:
            self.rotation_speed_x = 0.03
            self.pulse_speed = 0.08
            self.color = "#00ff00"
        elif "Spreken" in state:
            self.rotation_speed_x = 0.05
            self.pulse_speed = 0.2
            self.color = "#00ccff"
        elif "Nadenken" in state:
            self.rotation_speed_x = 0.08
            self.pulse_speed = 0.05
            self.color = "#ffaa00"
        elif "UIT" in state:
            self.rotation_speed_x = 0.005
            self.pulse_speed = 0.0
            self.color = "#333333"
        else:
            self.rotation_speed_x = 0.01
            self.pulse_speed = 0.05
            self.color = "#00ff00"

    def update(self):
        self.canvas.delete("wireframe")
        self.angle_x += self.rotation_speed_x
        self.angle_y += self.rotation_speed_y
        
        if self.pulse_speed > 0:
            self.pulse_val += self.pulse_speed
            intensity = 0.15 if self.pulse_speed > 0.1 else 0.05
            scale_factor = 1.0 + (math.sin(self.pulse_val) * intensity)
            self.radius = self.base_radius * scale_factor

        transformed_points = []
        cx_rot = math.cos(self.angle_x)
        sx_rot = math.sin(self.angle_x)
        cy_rot = math.cos(self.angle_y)
        sy_rot = math.sin(self.angle_y)

        for x, y, z in self.points:
            y_rot = y * cx_rot - z * sx_rot
            z_rot = y * sx_rot + z * cx_rot
            y = y_rot
            z = z_rot
            x_rot = x * cy_rot + z * sy_rot
            x = x_rot
            px = self.cx + x * self.radius
            py = self.cy + y * self.radius
            transformed_points.append((px, py))

        for p1_idx, p2_idx in self.lines:
            x1, y1 = transformed_points[p1_idx]
            x2, y2 = transformed_points[p2_idx]
            self.canvas.create_line(x1, y1, x2, y2, fill=self.color, width=1, tags="wireframe")

class KikuUI:
    def __init__(self, on_close_callback=None):
        self.on_close_callback = on_close_callback
        
        self.root = tk.Tk()
        self.root.title("Kiku AI Interface")
        self.root.attributes('-fullscreen', True)
        self.root.configure(background='black')
        
        self.root.bind('<Escape>', lambda e: self.on_close())
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        self.btn_exit = tk.Button(self.root, text="❌ SLUITEN", 
                                  command=self.on_close,
                                  bg='red', fg='white', font=("Arial", 12, "bold"),
                                  borderwidth=0, activebackground='#ff4444')
        self.btn_exit.place(relx=0.95, rely=0.05, anchor='ne')

        # --- CONTAINER VOOR VISUALS ---
        # We gebruiken één frame waar we OF de sphere OF de camera in tonen
        self.visual_frame = tk.Frame(self.root, bg='black', width=400, height=400)
        self.visual_frame.pack(pady=20)
        
        # 1. Canvas voor de Sphere
        self.canvas = tk.Canvas(self.visual_frame, width=400, height=400, bg='black', highlightthickness=0)
        self.canvas.pack() # Standaard zichtbaar
        self.sphere = WireframeSphere(self.canvas, center_x=200, center_y=200, radius=120, color='#00ff00')

        # 2. Label voor Camera Feed (Standaard verborgen)
        self.camera_label = tk.Label(self.visual_frame, bg='black')
        # We packen hem nog niet, dat doen we pas bij 'show_camera'

        # Status & Log
        self.label_status = tk.Label(self.root, text="KIKU ONLINE", 
                                     font=("Courier New", 24, "bold"), 
                                     bg='black', fg='#00ff00')
        self.label_status.pack(pady=10)

        self.text_area = scrolledtext.ScrolledText(self.root, 
                                                   font=("Consolas", 14), 
                                                   bg='black', fg='white',
                                                   insertbackground='white',
                                                   borderwidth=0, wrap=tk.WORD)
        self.text_area.pack(padx=50, pady=(0, 50), fill=tk.BOTH, expand=True)

        self.animate_sphere()

    def show_camera_feed(self, cv2_frame):
        """Toont een OpenCV beeld in de GUI."""
        # Verberg sphere als die er nog is
        self.canvas.pack_forget()
        self.camera_label.pack()

        # Convert kleuren van BGR (OpenCV) naar RGB (Tkinter)
        cv2image = cv2.cvtColor(cv2_frame, cv2.COLOR_BGR2RGB)
        
        # Maak plaatje van juiste grootte (400x300 bijv)
        img = Image.fromarray(cv2image)
        # Resize voor netheid als nodig
        img = img.resize((500, 375), Image.Resampling.LANCZOS)
        
        imgtk = ImageTk.PhotoImage(image=img)
        self.camera_label.imgtk = imgtk # Voorkom garbage collection
        self.camera_label.configure(image=imgtk)

    def show_sphere(self):
        """Terug naar de sphere modus."""
        self.camera_label.pack_forget()
        self.canvas.pack()

    def animate_sphere(self):
        try:
            self.sphere.update()
            self.root.after(30, self.animate_sphere)
        except:
            pass

    def update_status(self, text):
        self.label_status.config(text=text.upper())
        # Kleuren logica...
        fg_color = "#00ff00"
        if "UIT" in text: fg_color = "#555555"
        elif "Luisteren" in text: fg_color = "#00ff00"
        elif "Spreken" in text: fg_color = "#00ccff"
        elif "Nadenken" in text: fg_color = "#ffaa00"
        self.label_status.config(fg=fg_color)
        self.sphere.set_state(text)

    def log(self, text):
        self.text_area.insert(tk.END, text + "\n\n")
        self.text_area.see(tk.END)

    def start(self):
        self.root.mainloop()

    def on_close(self):
        if self.on_close_callback:
            self.on_close_callback()
        sys.exit(0)
