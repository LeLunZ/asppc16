from flask import Flask, request, jsonify, Response
from flask_socketio import SocketIO, emit

from models.dataholder import DataHolder

app = Flask(__name__)
socketio = SocketIO(app)

data = DataHolder()


@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'


@app.route('/api/data', methods=['POST'])
def all():
    if 'rain' in request.json:
        data.rain = request.json['rain']

    if 'light' in request.json:
        data.light = request.json['light']

    if 'wind' in request.json:
        data.wind = request.json['wind']

    if 'canopy_open' in request.json:
        data.canopy_open = request.json['canopy_open']

    if 'output_solar' in request.json:
        data.output_solar = request.json['output_solar']

    # TODO: check for thresholds

    emit('data', {
        'output_solar': data.output_solar,
        'light': data.light,
        'wind': data.wind,
        'rain': data.rain,
        'canopy_open': data.canopy_open
    })

    return Response(status=204)


@socketio.on('update_canopy')
def update_canopy(canopy_open):
    data.canopy_open = canopy_open
    # TODO: insert communication with raspberry

    emit('data', {
        'output_solar': data.output_solar,
        'light': data.light,
        'wind': data.wind,
        'rain': data.rain,
        'canopy_open': data.canopy_open
    })


@app.route('/api/data', methods=['GET'])
def get_data():
    return jsonify({
        'output_solar': data.output_solar,
        'light': data.light,
        'wind': data.wind,
        'rain': data.rain,
        'canopy_open': data.canopy_open
    })


@socketio.on('update_thresholds')
def update_data(min_light, max_wind, max_rain):
    data.min_light = min_light
    data.max_rain = max_rain
    data.max_wind = max_wind

    emit('thresholds', {
        'min_light': data.min_light,
        'max_wind': data.max_wind,
        'max_rain': data.max_rain
    })


@socketio.on('connection')
def connection():
    request.namespace.emit('data', {
        'output_solar': data.output_solar,
        'light': data.light,
        'wind': data.wind,
        'rain': data.rain,
        'canopy_open': data.canopy_open
    })


@app.route('/api/thresholds', methods=['POST'])
def thresholds():
    return jsonify({
        'min_light': data.min_light,
        'max_wind': data.max_wind,
        'max_rain': data.max_rain
    })


if __name__ == '__main__':
    socketio.run(app)
