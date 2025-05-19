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
    return render_template('index.html')

# Suppression des routes /goto_config et /teleporte_ball, ainsi que des fonctions associées

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
        print('Coordonnées reçues:', data)
        if 'points' not in data:
            data['points'] = points
        socketio.emit('update_coordinates', data)

if __name__ == '__main__':
    update_coordinates()  # Enregistre l'écouteur d'événements
    socketio.run(app, host='127.0.0.1', port=5000, debug=True,)