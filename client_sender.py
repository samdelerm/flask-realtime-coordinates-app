import socketio
import time
import rsk
import numpy as np

# Adresse et port du serveur Flask SocketIO
SERVER_URL = input("url page web")  # À adapter si le serveur est distant

# Crée un client SocketIO
sio = socketio.Client()

# Connexion au serveur
sio.connect(SERVER_URL)

# Exemple d'envoi de coordonnées et infos à intervalle régulier
def send_coordinates_loop():
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
    while True:
        try:
            with rsk.Client(input("quel ip gc")) as client:
                while True:
                    ball = to_tuple(client.ball)
                    blue1 = tuple(map(to_tuple, client.blue1.pose))
                    blue2 = tuple(map(to_tuple, client.blue2.pose))
                    green1 = tuple(map(to_tuple, client.green1.pose))
                    green2 = tuple(map(to_tuple, client.green2.pose))
                    # --- Correction de la logique highlight_point ---
                    xball, yball = ball
                    field_length = 1.84
                    field_width = 1.23
                    goal_width = 0.6
                    # Détection sortie terrain
                    out_of_field = not (-field_length/2 <= xball <= field_length/2 and -field_width/2 <= yball <= field_width/2)
                    # Détection but
                    but_bleu = (xball > field_length/2 - 0.003) and (abs(yball) < goal_width/2)
                    but_vert = (xball < -field_length/2 + 0.003) and (abs(yball) < goal_width/2)
                    is_goal = but_bleu or but_vert
                    # Calcul du highlight_point uniquement si balle sortie ET pas but
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
                    # Gestion robuste du referee
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
                        print("Erreur referee:", e)
                    data = {
                        'ball': ball,
                        'blue1': blue1,
                        'blue2': blue2,
                        'green1': green1,
                        'green2': green2,
                        'points': points,
                        'blue_team_name': blue_team_name,
                        'green_team_name': green_team_name,
                        'blue_score': blue_score,
                        'green_score': green_score,
                        'highlight_point': highlight_point
                    }
                    sio.emit('update_coordinates', data)
                    print('Coordonnées envoyées:', data)
                    time.sleep(0.005)  # Pause de 5 ms pour éviter la saturation
        except Exception as e:
            print('Erreur rsk.Client ou envoi:', e)
            time.sleep(0.5)

if __name__ == '__main__':
    try:
        send_coordinates_loop()
    except KeyboardInterrupt:
        print("Arrêté par l'utilisateur")
        sio.disconnect()
