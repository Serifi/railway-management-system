import os
from flask import Blueprint, request, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.carriage import Carriage, Railcar, PassengerCar
from models.train import TrainPassengerCars, Train
from models import Base

carriage_blueprint = Blueprint('carriage_routes', __name__)

DATABASE_URL = f"sqlite:///{os.path.abspath('server/db/fleet.db')}"
engine = create_engine(DATABASE_URL, echo=False)
Session = sessionmaker(bind=engine)
Base.metadata.create_all(engine)

@carriage_blueprint.route('/', methods=['GET'])
def get_all_carriages():
    session = Session()
    railcars = session.query(Railcar).all()
    p_cars = session.query(PassengerCar).all()

    # Combine results
    railcar_list = [{
        "carriageID": r.carriageID,
        "trackGauge": r.carriage.trackGauge,
        "type": "Railcar",
        "maxTractiveForce": r.maxTractiveForce
    } for r in railcars]

    p_car_list = [{
        "carriageID": p.carriageID,
        "trackGauge": p.carriage.trackGauge,
        "type": "PassengerCar",
        "numberOfSeats": p.numberOfSeats,
        "maxWeight": p.maxWeight
    } for p in p_cars]

    return jsonify(railcar_list + p_car_list), 200

@carriage_blueprint.route('/<int:carriage_id>', methods=['GET'])
def get_carriage_by_id(carriage_id):
    session = Session()
    r = session.query(Railcar).filter_by(carriageID=carriage_id).first()
    p = session.query(PassengerCar).filter_by(carriageID=carriage_id).first()

    if not r and not p:
        return jsonify({"message": f"Carriage {carriage_id} not found"}), 404

    if r:
        return jsonify({
            "carriageID": r.carriageID,
            "trackGauge": r.carriage.trackGauge,
            "type": "Railcar",
            "maxTractiveForce": r.maxTractiveForce
        }), 200
    else:
        return jsonify({
            "carriageID": p.carriageID,
            "trackGauge": p.carriage.trackGauge,
            "type": "PassengerCar",
            "numberOfSeats": p.numberOfSeats,
            "maxWeight": p.maxWeight
        }), 200

@carriage_blueprint.route('/', methods=['POST'])
def create_carriage():
    data = request.get_json()
    if not data or not data.get('trackGauge') or not data.get('type'):
        return jsonify({"message": "Missing trackGauge or type"}), 400

    if data['trackGauge'] not in ['1435', '1000']:
        return jsonify({"message": "trackGauge must be 1435 or 1000"}), 400

    new_c = Carriage(trackGauge=data['trackGauge'], type=data['type'])
    session = Session()

    # Create railcar or passengerCar
    if data['type'] == "Railcar":
        if 'maxTractiveForce' not in data:
            return jsonify({"message": "maxTractiveForce required for Railcar"}), 400
        new_r = Railcar(carriage=new_c, maxTractiveForce=data['maxTractiveForce'])
        session.add(new_r)
    elif data['type'] == "PassengerCar":
        if 'numberOfSeats' not in data or 'maxWeight' not in data:
            return jsonify({"message": "numberOfSeats and maxWeight required for PassengerCar"}), 400
        new_p = PassengerCar(carriage=new_c,
                             numberOfSeats=data['numberOfSeats'],
                             maxWeight=data['maxWeight'])
        session.add(new_p)
    else:
        return jsonify({"message": "Invalid carriage type"}), 400

    session.commit()
    return jsonify({"message": "Carriage created"}), 201

@carriage_blueprint.route('/<int:carriageID>', methods=['PUT'])
def update_carriage(carriageID):
    data = request.get_json()
    session = Session()
    c = session.query(Carriage).filter_by(carriageID=carriageID).first()
    if not c:
        return jsonify({"message": "Carriage not found"}), 404

    # Check if carriage is in a train
    in_train = session.query(TrainPassengerCars).filter_by(passengerCarID=carriageID).first() \
               or session.query(Train).filter_by(railcarID=carriageID).first()
    if in_train:
        return jsonify({"message": "Cannot edit carriage currently assigned to a train"}), 400

    if 'trackGauge' in data:
        c.trackGauge = data['trackGauge']
    if 'type' in data:
        c.type = data['type']

    if c.type == "Railcar":
        r = session.query(Railcar).filter_by(carriageID=carriageID).first()
        if 'maxTractiveForce' in data:
            r.maxTractiveForce = data['maxTractiveForce']
    else:
        p = session.query(PassengerCar).filter_by(carriageID=carriageID).first()
        if 'numberOfSeats' in data:
            p.numberOfSeats = data['numberOfSeats']
        if 'maxWeight' in data:
            p.maxWeight = data['maxWeight']

    session.commit()
    return jsonify({"message": "Carriage updated"}), 200

@carriage_blueprint.route('/<int:carriageID>', methods=['DELETE'])
def delete_carriage(carriageID):
    session = Session()
    c = session.query(Carriage).filter_by(carriageID=carriageID).first()
    if not c:
        return jsonify({"message": "Carriage not found"}), 404

    # Check if carriage is in a train
    in_train = session.query(TrainPassengerCars).filter_by(passengerCarID=carriageID).first() \
               or session.query(Train).filter_by(railcarID=carriageID).first()
    if in_train:
        return jsonify({"message": "Cannot delete carriage assigned to a train"}), 400

    if c.type == "Railcar":
        r = session.query(Railcar).filter_by(carriageID=carriageID).first()
        session.delete(r)
    else:
        p = session.query(PassengerCar).filter_by(carriageID=carriageID).first()
        session.delete(p)

    session.delete(c)
    session.commit()
    return jsonify({"message": "Carriage deleted"}), 200