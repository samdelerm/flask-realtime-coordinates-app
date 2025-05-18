from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO
import rsk
from concurrent.futures import ProcessPoolExecutor

app = Flask(__name__)
socketio = SocketIO(app)
executor = ProcessPoolExecutor()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/goto_config', methods=['POST'])
def goto_config():
    data = request.get_json()
    config = data.get('config', 'game')
    executor.submit(run_goto_config, config)
    return '', 204

def run_goto_config(config):
    with rsk.Client() as client:
        client.goto_configuration(config, wait=False)

def update_coordinates():
    points = {
        'point1': (0.45, 0.3),
        'point2': (-0.45, 0.3),
        'point3': (-0.45, -0.3),
        'point4': (0.45, -0.3)
    }
    with rsk.Client() as client:
        while True:
            xball, yball = client.ball
            xblue1, yblue1, alblue1 = client.blue1.pose
            xblue2, yblue2, alblue2 = client.blue2.pose
            xgreen1, ygreen1, algreen1 = client.green1.pose
            xgreen2, ygreen2, algreen2 = client.green2.pose
            # Récupération des noms d'équipe
            try:
                blue_team_name = client.referee["teams"]["blue"]["name"]
            except Exception as e:
                blue_team_name = "Bleu"
                print(e)
            try:
                green_team_name = client.referee["teams"]["green"]["name"]
            except Exception as e:
                green_team_name = "Vert"
                print(e)
            coordinates = {
                'ball': (xball, yball),
                'blue1': (xblue1, yblue1, alblue1),
                'blue2': (xblue2, yblue2, alblue2),
                'green1': (xgreen1, ygreen1, algreen1),
                'green2': (xgreen2, ygreen2, algreen2),
                'points': points,
                'blue_team_name': blue_team_name,
                'green_team_name': green_team_name
            }
            # Nouvelle logique de sortie
            sortie = False
            but = False
            # Sortie si y > 0.63 ou y < -0.63
            if abs(yball) > 0.63:
                sortie = True
            # Sortie si x > 0.92 ou x < -0.92 ET y dans [0.3, 0.63] ou [-0.3, -0.63]
            elif abs(xball) > 0.92 and (0.3 <= abs(yball) <= 0.63):
                sortie = True
            # But si x > 0.92 ou x < -0.92 ET y dans [-0.3, 0.3]
            elif abs(xball) > 0.92 and abs(yball) < 0.3:
                but = True
            if sortie and not but:
                # Trouver le point le plus proche de la sortie
                min_dist = float('inf')
                closest_point = None
                for name, (px, py) in points.items():
                    dist = ((xball - px)**2 + (yball - py)**2)**0.5
                    if dist < min_dist:
                        min_dist = dist
                        closest_point = name
                coordinates['highlight_point'] = closest_point
            else:
                coordinates['highlight_point'] = None
            socketio.emit('update_coordinates', coordinates)
            socketio.sleep(0.001)

if __name__ == '__main__':
    socketio.start_background_task(update_coordinates)
    socketio.run(app)