from flask import Flask, Blueprint, request, jsonify
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from models.Carriage import Carriage, Railcar, PassengerCar
import os

DATABASE_URL = f"sqlite:///{os.path.abspath('server/db/fleet.db')}"
engine = create_engine(DATABASE_URL, echo=True)
Session = sessionmaker(bind=engine)
Base = declarative_base()

Base.metadata.create_all(engine)

carriage_blueprint = Blueprint('carriage_routes', __name__)

@carriage_blueprint.route('/', methods=['GET'])
def get_all_carriages():
    session = Session()

    railcars = session.query(Railcar).all()
    passenger_cars = session.query(PassengerCar).all()

    railcar_list = [
        {
            "carriageID": railcar.carriageID,
            "trackGauge": railcar.carriage.trackGauge,
            "type": "Railcar",
            "maxTractiveForce": railcar.maxTractiveForce
        }
        for railcar in railcars
    ]

    passenger_car_list = [
        {
            "carriageID": passenger_car.carriageID,
            "trackGauge": passenger_car.carriage.trackGauge,
            "type": "PassengerCar",
            "numberOfSeats": passenger_car.numberOfSeats,
            "maxWeight": passenger_car.maxWeight
        }
        for passenger_car in passenger_cars
    ]

    all_carriages = railcar_list + passenger_car_list
    return jsonify(all_carriages)

@carriage_blueprint.route('/<int:carriage_id>', methods=['GET'])
def get_carriage_by_id(carriage_id):
    session = Session()

    railcar = session.query(Railcar).filter(Railcar.carriageID == carriage_id).first()
    passenger_car = session.query(PassengerCar).filter(PassengerCar.carriageID == carriage_id).first()

    if not railcar and not passenger_car:
        return jsonify({"message": f"Carriage mit ID {carriage_id} nicht gefunden"}), 404

    if railcar:
        return jsonify({
            "carriageID": railcar.carriageID,
            "trackGauge": railcar.carriage.trackGauge,
            "type": "Railcar",
            "maxTractiveForce": railcar.maxTractiveForce
        })

    if passenger_car:
        return jsonify({
            "carriageID": passenger_car.carriageID,
            "trackGauge": passenger_car.carriage.trackGauge,
            "type": "PassengerCar",
            "numberOfSeats": passenger_car.numberOfSeats,
            "maxWeight": passenger_car.maxWeight
        })


@carriage_blueprint.route('/', methods=['POST'])
def create_carriage():
    data = request.get_json()

    if not data or not data.get('trackGauge') or not data.get('type'):
        return jsonify({"message": "Fehlende Daten: 'trackGauge' und 'type' werden benötigt"}), 400

    track_gauge_value = data['trackGauge']

    if track_gauge_value not in ['1435', '1000']:
        return jsonify({"message": "Ungültiger Wert für 'trackGauge'. Erlaubte Werte: '1435' oder '1000'"}), 400

    new_carriage = Carriage(trackGauge=track_gauge_value, type=data['type'])

    session = Session()

    if data['type'] == "Railcar":
        if 'maxTractiveForce' not in data:
            return jsonify({"message": "Fehlende Daten: 'maxTractiveForce' wird für Railcar benötigt"}), 400
        new_railcar = Railcar(carriage=new_carriage, maxTractiveForce=data['maxTractiveForce'])
        session.add(new_railcar)
    elif data['type'] == "PassengerCar":
        if 'numberOfSeats' not in data or 'maxWeight' not in data:
            return jsonify(
                {"message": "Fehlende Daten: 'numberOfSeats' und 'maxWeight' werden für PassengerCar benötigt"}), 400
        new_passenger_car = PassengerCar(carriage=new_carriage, numberOfSeats=data['numberOfSeats'],
                                         maxWeight=data['maxWeight'])
        session.add(new_passenger_car)
    else:
        return jsonify({"message": "Ungültiger Wagentyp. Erlaubte Typen: 'Railcar' oder 'PassengerCar'"}), 400

    session.commit()

    return jsonify({
        "carriageID": new_carriage.carriageID,
        "trackGauge": new_carriage.trackGauge,
        "type": new_carriage.type,
        "maxTractiveForce" if 'maxTractiveForce' in data else "numberOfSeats": data.get('maxTractiveForce',
                                                                                        data.get('numberOfSeats')),
        "maxWeight": data.get('maxWeight')
    }), 201


@carriage_blueprint.route('/<int:carriageID>', methods=['PUT'])
def update_carriage(carriageID):
    data = request.get_json()
    session = Session()

    carriage = session.query(Carriage).filter(Carriage.carriageID == carriageID).first()

    if not carriage:
        return jsonify({"message": "Carriage not found"}), 404

    if 'trackGauge' in data:
        carriage.trackGauge = data['trackGauge']

    if 'type' in data:
        carriage.type = data['type']

    if carriage.type == "Railcar":
        railcar = session.query(Railcar).filter(Railcar.carriageID == carriageID).first()
        if 'maxTractiveForce' in data:
            railcar.maxTractiveForce = data['maxTractiveForce']
    elif carriage.type == "PassengerCar":
        passenger_car = session.query(PassengerCar).filter(PassengerCar.carriageID == carriageID).first()
        if 'numberOfSeats' in data:
            passenger_car.numberOfSeats = data['numberOfSeats']
        if 'maxWeight' in data:
            passenger_car.maxWeight = data['maxWeight']

    session.commit()

    return jsonify({
        "carriageID": carriage.carriageID,
        "trackGauge": carriage.trackGauge,
        "type": carriage.type,
        "maxTractiveForce" if carriage.type == "Railcar" else "numberOfSeats": data.get('maxTractiveForce', data.get('numberOfSeats')),
        "maxWeight": data.get('maxWeight')
    }), 200


@carriage_blueprint.route('/<int:carriageID>', methods=['DELETE'])
def delete_carriage(carriageID):
    session = Session()

    carriage = session.query(Carriage).filter(Carriage.carriageID == carriageID).first()

    if not carriage:
        return jsonify({"message": "Carriage not found"}), 404

    if carriage.type == "Railcar":
        railcar = session.query(Railcar).filter(Railcar.carriageID == carriageID).first()
        session.delete(railcar)
    elif carriage.type == "PassengerCar":
        passenger_car = session.query(PassengerCar).filter(PassengerCar.carriageID == carriageID).first()
        session.delete(passenger_car)

    session.delete(carriage)
    session.commit()

    return jsonify({"message": "Carriage deleted successfully"}), 200
