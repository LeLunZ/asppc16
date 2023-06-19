from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from flask_cors import CORS
from threading import Thread
from eventlet import sleep
from main import main_controller
from sensors import MAX_WIND
from math import isnan

BROADCAST_FREQ = 1 # seconds

app = Flask(__name__, static_folder='./templates')
CORS(app)
socketio = SocketIO(app, cors_allowed_origins='*', async_mode='eventlet')


@app.route('/', methods=['GET'])
def main_page():
    return render_template('index.html')
    
def broadcast_update():
    socketio.emit('update', main_controller.data_to_dict(), broadcast=True)
    
def regular_update():
    while True:
        broadcast_update()
        sleep(BROADCAST_FREQ)

@socketio.on('manual_open')
def manual_open():
    main_controller.manualOpen = True
    main_controller.manual = True
    main_controller.update()
    broadcast_update()

@socketio.on('manual_close')
def manual_close():
    main_controller.manualOpen = False
    main_controller.manual = True
    main_controller.update()
    broadcast_update()

@socketio.on('manual_off')
def manual_off():
    main_controller.manual = False
    main_controller.update()
    broadcast_update()

@socketio.on('request_update')
def request_update():
    emit('update', main_controller.data_to_dict())

@socketio.on('update_wind_lower_threshold')
def update_wind_lower_threshold(threshold):
    threshold = float(threshold)
    if isnan(threshold):
        emit('error', 'Invalid value: wind_lower_threshold')
        return
    if threshold > main_controller.wind_upper_threshold:
        emit('error', 'wind_lower_threshold > wind_upper_threshold')
        return
    if not (0 <= threshold <= MAX_WIND):
        emit('error', 'Out of range: wind_lower_threshold')
        return
    main_controller.wind_lower_threshold = threshold
    main_controller.update()
    broadcast_update()

@socketio.on('update_wind_upper_threshold')
def update_wind_upper_threshold(threshold):
    threshold = float(threshold)
    if isnan(threshold):
        emit('error', 'Invalid value: wind_upper_threshold')
        return
    if threshold < main_controller.wind_lower_threshold:
        emit('error', 'wind_upper_threshold < wind_lower_threshold')
        return
    if not (0 <= threshold <= MAX_WIND):
        emit('error', 'Out of range: wind_upper_threshold')
        return
    main_controller.wind_upper_threshold = threshold
    main_controller.update()
    broadcast_update()

@socketio.on('update_precipitation_lower_threshold')
def update_precipitation_lower_threshold(threshold):
    threshold = float(threshold)
    if isnan(threshold):
        emit('error', 'Invalid value: precipitation_lower_threshold')
        return
    if threshold > main_controller.precipitation_upper_threshold:
        emit('error', 'precipitation_lower_threshold > precipitation_upper_threshold')
        return
    if not (0 <= threshold <= 1):
        emit('error', 'Out of range: precipitation_lower_threshold')
        return
    main_controller.precipitation_lower_threshold = threshold
    main_controller.update()
    broadcast_update()

@socketio.on('update_precipitation_upper_threshold')
def update_precipitation_upper_threshold(threshold):
    threshold = float(threshold)
    if isnan(threshold):
        emit('error', 'Invalid value: precipitation_upper_threshold')
        return
    if threshold < main_controller.precipitation_lower_threshold:
        emit('error', 'precipitation_upper_threshold < precipitation_lower_threshold')
        return
    if not (0 <= threshold <= 1):
        emit('error', 'Out of range: precipitation_upper_threshold')
        return
    main_controller.precipitation_upper_threshold = threshold
    main_controller.update()
    broadcast_update()

@socketio.on('update_light_lower_threshold')
def update_light_lower_threshold(threshold):
    threshold = float(threshold)
    if isnan(threshold):
        emit('error', 'Invalid value: light_lower_threshold')
        return
    if threshold > main_controller.light_upper_threshold:
        emit('error', 'light_lower_threshold > light_upper_threshold')
        return
    if not (0 <= threshold <= 1):
        emit('error', 'Out of range: light_lower_threshold')
        return
    main_controller.light_lower_threshold = threshold
    main_controller.update()
    broadcast_update()

@socketio.on('update_light_upper_threshold')
def update_light_upper_threshold(threshold):
    threshold = float(threshold)
    if isnan(threshold):
        emit('error', 'Invalid value: light_upper_threshold')
        return
    if threshold < main_controller.light_lower_threshold:
        emit('error', 'light_upper_threshold < light_lower_threshold')
        return
    if not (0 <= threshold <= 1):
        emit('error', 'Out of range: light_upper_threshold')
        return
    main_controller.light_upper_threshold = threshold
    main_controller.update()
    broadcast_update()

if __name__ == '__main__':
    print("starting server")
    socketio.start_background_task(regular_update)
    socketio.run(app, host="192.168.0.1", port=80)
