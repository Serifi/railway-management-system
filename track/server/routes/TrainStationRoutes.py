from flask import Blueprint, jsonify, request
from models.TrainStation import TrainStation
from models.Section import Section
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
import os

DATABASE_URL = f"sqlite:///{os.path.abspath('server/db/track.db')}"
engine = create_engine(DATABASE_URL, echo=True)
Session = sessionmaker(bind=engine)

trainstation_blueprint = Blueprint('trainstation_routes', __name__)

@trainstation_blueprint.route('/', methods=['GET'])
def get_trainstations():
    session = Session()
    stations = session.query(TrainStation).all()
    stations_list = [{'stationID': station.stationID, 'stationName': station.stationName, 'address': station.address} for station in stations]
    return jsonify(stations_list)

@trainstation_blueprint.route('/<int:station_id>', methods=['GET'])
def get_trainstation_by_id(station_id):
    session = Session()
    station = session.query(TrainStation).filter(TrainStation.stationID == station_id).first()
    if not station:
        return jsonify({"message": f"Bahnhof mit ID {station_id} nicht gefunden"}), 404
    return jsonify({'stationID': station.stationID, 'stationName': station.stationName, 'address': station.address})

@trainstation_blueprint.route('/', methods=['POST'])
def create_trainstation():
    data = request.get_json()
    if not data or not all(key in data for key in ['stationName', 'address']):
        return jsonify({"message": "Fehlende Daten: 'stationName' und 'address' werden benötigt"}), 400

    session = Session()
    try:
        new_station = TrainStation(stationName=data['stationName'], address=data['address'])
        session.add(new_station)
        session.commit()
        return jsonify({'stationID': new_station.stationID, 'stationName': new_station.stationName, 'address': new_station.address}), 201
    except ValueError as e:
        return jsonify({"message": str(e)}), 400
    except IntegrityError:
        session.rollback()
        return jsonify({"message": "Der Name des Bahnhofs muss eindeutig sein"}), 400

@trainstation_blueprint.route('/<int:station_id>', methods=['PUT'])
def update_trainstation(station_id):
    data = request.get_json()
    if not data:
        return jsonify({"message": "Es wurden keine Daten übermittelt"}), 400

    session = Session()
    station = session.query(TrainStation).filter(TrainStation.stationID == station_id).first()
    if not station:
        return jsonify({"message": f"Bahnhof mit ID {station_id} nicht gefunden"}), 404

    sections_in_use = session.query(Section).filter(
        (Section.startStationID == station_id) | (Section.endStationID == station_id)
    ).first()
    if sections_in_use:
        return jsonify({"message": "Bahnhof ist aktuell in Verwendung und kann nicht bearbeitet werden"}), 400

    try:
        if 'stationName' in data:
            station.stationName = data['stationName']
        if 'address' in data:
            station.address = data['address']
        session.commit()
        return jsonify({'stationID': station.stationID, 'stationName': station.stationName, 'address': station.address}), 200
    except ValueError as e:
        return jsonify({"message": str(e)}), 400
    except IntegrityError:
        session.rollback()
        return jsonify({"message": "Der Name des Bahnhofs muss eindeutig sein"}), 400

@trainstation_blueprint.route('/<int:station_id>', methods=['DELETE'])
def delete_trainstation(station_id):
    session = Session()
    station = session.query(TrainStation).filter(TrainStation.stationID == station_id).first()
    if not station:
        return jsonify({"message": f"Bahnhof mit ID {station_id} nicht gefunden"}), 404

    sections_in_use = session.query(Section).filter(
        (Section.startStationID == station_id) | (Section.endStationID == station_id)
    ).first()
    if sections_in_use:
        return jsonify({"message": "Bahnhof ist aktuell in Verwendung und kann nicht gelöscht werden"}), 400

    session.delete(station)
    session.commit()
    return jsonify({"message": f"Bahnhof mit ID {station_id} wurde erfolgreich gelöscht"}), 200