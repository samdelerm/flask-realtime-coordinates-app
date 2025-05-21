import eventlet
eventlet.monkey_patch()
from flask import Flask, render_template, request
from flask_socketio import SocketIO
import rsk
from concurrent.futures import ProcessPoolExecutor
import eventlet.wsgi

app = Flask(__name__)
socketio = SocketIO(app)
executor = ProcessPoolExecutor()

@app.route('/')
def index():
    terrains = [
        {
            'name': f'Terrain {i+1}',
            'desc': f'Voir la vue 3D du terrain {i+1}',
            'url': f'/terrain{i+1}'
        }
        for i in range(10)
    ]
    return render_template('index.html', terrains=terrains)

@app.route('/terrain<int:terrain_id>')
def terrain_view(terrain_id):
    # Affiche la page 3D du terrain avec la banderole
    return render_template('terrain3d.html', terrain_id=terrain_id)

def update_coordinates():
    points = {
        'point1': (0.45, 0.3),
        'point2': (-0.45, 0.3),
        'point3': (-0.45, -0.3),
        'point4': (0.45, -0.3)
    }
    # On écoute les coordonnées envoyées par un client distant
    @socketio.on('update_coordinates')
    def handle_update_coordinates(data):
        # On attend un champ 'terrain_id' dans les données
        terrain_id = data.get('terrain_id')
        print(f"Coordonnées reçues pour terrain {terrain_id}:", data)
        if 'points' not in data:
            data['points'] = points
        # Vérification du type de terrain_id (doit être int ou str convertible en int)
        try:
            terrain_id_int = int(terrain_id)
        except (TypeError, ValueError):
            print(f"terrain_id invalide: {terrain_id}")
            return
        if terrain_id_int is not None:
            socketio.emit(f'update_coordinates_{terrain_id_int}', data, room=f'terrain{terrain_id_int}')

    @socketio.on('join_terrain')
    def handle_join_terrain(data):
        terrain_id = data.get('terrain_id')
        try:
            terrain_id_int = int(terrain_id)
        except (TypeError, ValueError):
            print(f"terrain_id invalide (join): {terrain_id}")
            return
        room = f'terrain{terrain_id_int}'
        from flask_socketio import join_room
        join_room(room)
        print(f"Client {request.sid} rejoint la room {room}")

if __name__ == '__main__':
    update_coordinates()  # Enregistre l'écouteur d'événements
    socketio.run(app, host='127.0.0.1', port=1000, debug=True,)