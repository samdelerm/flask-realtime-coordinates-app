import socketio
import time
import rsk
import numpy as np
import tkinter as tk
from tkinter import ttk
import threading
import queue

# Adresse et port du serveur Flask SocketIO

# Exemple d'envoi de coordonnées et infos à intervalle régulier

class ClientSenderGUI:
    def __init__(self, master):
        self.master = master
        master.title("Client Sender - Robotique")
        self.running = False
        self.send_thread = None
        self.msg_queue = queue.Queue()
        # Variables
        self.server_url = tk.StringVar(value="http://localhost:5000")
        self.rsk_ip = tk.StringVar(value="rsk.simulateur.les-amicales.fr")
        self.send_speed = tk.DoubleVar(value=0.005)
        self.terrain_id = tk.IntVar(value=1)  # Ajout du terrain sélectionné
        self.last_data = tk.StringVar(value="")
        # Layout
        frm = ttk.Frame(master, padding=18, style="Main.TFrame")
        frm.grid(row=0, column=0, sticky="nsew")
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Main.TFrame", background="#e3f2fd")
        style.configure("TLabel", background="#e3f2fd", font=("Segoe UI", 11))
        style.configure("TButton", font=("Segoe UI", 11, "bold"), padding=6)
        style.configure("TEntry", font=("Segoe UI", 11))
        style.map("TButton", background=[('active', '#1976d2')], foreground=[('active', '#fff')])
        # Titre
        title = ttk.Label(frm, text="Client Sender - Robotique", font=("Segoe UI", 16, "bold"), background="#1976d2", foreground="#fff", anchor="center")
        title.grid(row=0, column=0, columnspan=2, pady=(0, 18), sticky="ew")
        ttk.Label(frm, text="URL serveur Flask-SocketIO :").grid(row=1, column=0, sticky="w")
        ttk.Entry(frm, textvariable=self.server_url, width=40, style="TEntry").grid(row=1, column=1, sticky="ew")
        ttk.Label(frm, text="IP rsk.Client :").grid(row=2, column=0, sticky="w")
        ttk.Entry(frm, textvariable=self.rsk_ip, width=40, style="TEntry").grid(row=2, column=1, sticky="ew")
        ttk.Label(frm, text="Vitesse d'envoi (s) :").grid(row=3, column=0, sticky="w")
        tk.Scale(frm, from_=0.001, to=0.1, variable=self.send_speed, orient="horizontal", length=200, resolution=0.001, digits=3, label="Vitesse d'envoi (s)", bg="#e3f2fd", highlightthickness=0, troughcolor="#90caf9", sliderrelief="flat").grid(row=3, column=1, sticky="ew")
        # Sélecteur de terrain
        ttk.Label(frm, text="Numéro du terrain (1-10) :").grid(row=4, column=0, sticky="w")
        terrain_spin = ttk.Spinbox(frm, from_=1, to=10, textvariable=self.terrain_id, width=5, font=("Segoe UI", 11))
        terrain_spin.grid(row=4, column=1, sticky="w")
        self.start_btn = ttk.Button(frm, text="Démarrer", command=self.start_sending, style="TButton")
        self.start_btn.grid(row=5, column=0, pady=10)
        self.stop_btn = ttk.Button(frm, text="Arrêter", command=self.stop_sending, state="disabled", style="TButton")
        self.stop_btn.grid(row=5, column=1, pady=10)
        ttk.Label(frm, text="Coordonnées transmises :", font=("Segoe UI", 11, "bold")).grid(row=6, column=0, sticky="w", pady=(10,0))
        self.data_text = tk.Text(frm, height=8, width=60, state="disabled", bg="#f5faff", fg="#263238", font=("Consolas", 10), relief="flat", highlightthickness=1, highlightbackground="#90caf9")
        self.data_text.grid(row=7, column=0, columnspan=2, sticky="ew", pady=(0,10))
        frm.columnconfigure(1, weight=1)
        # Boucle d'affichage
        self.master.configure(bg="#e3f2fd")
        self.master.after(100, self.update_gui)

    def start_sending(self):
        self.running = True
        self.start_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        self.send_thread = threading.Thread(target=self.send_coordinates_loop, daemon=True)
        self.send_thread.start()

    def stop_sending(self):
        self.running = False
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")

    def update_gui(self):
        try:
            while True:
                msg = self.msg_queue.get_nowait()
                self.data_text.config(state="normal")
                self.data_text.delete(1.0, tk.END)
                self.data_text.insert(tk.END, msg)
                self.data_text.config(state="disabled")
        except queue.Empty:
            pass
        self.master.after(100, self.update_gui)

    def send_coordinates_loop(self):
        import socketio
        import rsk
        import numpy as np
        sio = socketio.Client()
        try:
            sio.connect(self.server_url.get())
        except Exception as e:
            self.msg_queue.put(f"Erreur connexion serveur: {e}")
            self.stop_sending()
            return
        points = {
            'point1': (0.45, 0.3),
            'point2': (-0.45, 0.3),
            'point3': (-0.45, -0.3),
            'point4': (0.45, -0.3)
        }
        def to_tuple(x):
            if isinstance(x, np.ndarray):
                return tuple(x.tolist())
            if isinstance(x, (list, tuple)):
                return tuple(x)
            return x
        while self.running:
            try:
                with rsk.Client(self.rsk_ip.get()) as client:
                    while self.running:
                        ball = to_tuple(client.ball)
                        blue1 = tuple(map(to_tuple, client.blue1.pose))
                        blue2 = tuple(map(to_tuple, client.blue2.pose))
                        green1 = tuple(map(to_tuple, client.green1.pose))
                        green2 = tuple(map(to_tuple, client.green2.pose))
                        xball, yball = ball
                        field_length = 1.84
                        field_width = 1.23
                        goal_width = 0.6
                        out_of_field = not (-field_length/2 <= xball <= field_length/2 and -field_width/2 <= yball <= field_width/2)
                        but_bleu = (xball > field_length/2 - 0.003) and (abs(yball) < goal_width/2)
                        but_vert = (xball < -field_length/2 + 0.003) and (abs(yball) < goal_width/2)
                        is_goal = but_bleu or but_vert
                        highlight_point = None
                        if out_of_field and not is_goal:
                            min_dist = float('inf')
                            closest_point = None
                            for name, (px, py) in points.items():
                                dist = ((xball - px)**2 + (yball - py)**2)**0.5
                                if dist < min_dist:
                                    min_dist = dist
                                    closest_point = name
                            highlight_point = closest_point
                        blue_team_name = 'Bleu'
                        green_team_name = 'Vert'
                        blue_score = 0
                        green_score = 0
                        try:
                            blue_team_name = client.referee["teams"]["blue"]['name'] if client.referee["teams"]["blue"]["name"] is not None else 'Bleu'
                            green_team_name = client.referee["teams"]["green"]['name'] if client.referee["teams"]["green"]["name"] is not None else 'Vert'
                            blue_score = int(client.referee["teams"]["blue"]["score"]) if client.referee["teams"]["blue"]["score"] is not None else 0
                            green_score = int(client.referee["teams"]["green"]["score"]) if client.referee["teams"]["green"]["score"] is not None else 0
                        except Exception as e:
                            pass
                        data = {
                            'blue1': blue1,
                            'blue2': blue2,
                            'green1': green1,
                            'green2': green2,
                            'ball': ball,
                            'points': points,
                            'blue_team_name': blue_team_name,
                            'green_team_name': green_team_name,
                            'blue_score': blue_score,
                            'green_score': green_score,
                            'highlight_point': highlight_point,
                            'terrain_id': self.terrain_id.get()  # Utilise la valeur choisie dans l'interface
                        }
                        sio.emit('update_coordinates', data)
                        self.msg_queue.put(str(data))
                        time.sleep(self.send_speed.get())
            except Exception as e:
                self.msg_queue.put(f"Erreur rsk.Client ou envoi: {e}")
                time.sleep(0.5)
        sio.disconnect()

if __name__ == '__main__':
    root = tk.Tk()
    app = ClientSenderGUI(root)
    root.mainloop()
