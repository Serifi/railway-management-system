from flask import Blueprint, jsonify, request
from models.TrainStation import TrainStation, Session

trainstation_blueprint = Blueprint('trainstation_routes', __name__)

@trainstation_blueprint.route('/', methods=['GET'])
def get_trainstations():
    session = Session()
    stations = session.query(TrainStation).all()

    stations_list = [
        {
            'stationID': station.stationID,
            'stationName': station.stationName,
            'address': station.address
        }
        for station in stations
    ]

    return jsonify(stations_list)

@trainstation_blueprint.route('/<int:station_id>', methods=['GET'])
def get_trainstation_by_id(station_id):
    session = Session()
    station = session.query(TrainStation).filter(TrainStation.stationID == station_id).first()

    if not station:
        return jsonify({"message": f"TrainStation mit ID {station_id} nicht gefunden"}), 404

    return jsonify({
        'stationID': station.stationID,
        'stationName': station.stationName,
        'address': station.address
    })

@trainstation_blueprint.route('/', methods=['POST'])
def create_trainstation():
    data = request.get_json()

    if not data or not data.get('stationName') or not data.get('address'):
        return jsonify({"message": "Fehlende Daten: 'stationName' und 'address' werden benötigt"}), 400

    new_station = TrainStation(
        stationName=data['stationName'],
        address=data['address']
    )

    session = Session()
    session.add(new_station)
    session.commit()

    return jsonify({
        'stationID': new_station.stationID,
        'stationName': new_station.stationName,
        'address': new_station.address
    }), 201

@trainstation_blueprint.route('/<int:station_id>', methods=['PUT'])
def update_trainstation(station_id):
    data = request.get_json()

    session = Session()
    station = session.query(TrainStation).filter(TrainStation.stationID == station_id).first()

    if not station:
        return jsonify({"message": f"Station mit ID {station_id} nicht gefunden"}), 404

    if 'stationName' in data:
        station.stationName = data['stationName']
    if 'address' in data:
        station.address = data['address']

    session.commit()

    return jsonify({
        'stationID': station.stationID,
        'stationName': station.stationName,
        'address': station.address
    }), 200

@trainstation_blueprint.route('/<int:station_id>', methods=['DELETE'])
def delete_trainstation(station_id):
    session = Session()
    station = session.query(TrainStation).filter(TrainStation.stationID == station_id).first()

    if not station:
        return jsonify({"message": f"Station mit ID {station_id} nicht gefunden"}), 404

    session.delete(station)
    session.commit()

    return jsonify({"message": f"Station mit ID {station_id} wurde erfolgreich gelöscht"}), 200
