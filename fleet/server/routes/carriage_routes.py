# carriage_routes.py
from flask import Blueprint, request, jsonify
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload
from . import SessionLocal
from models.carriage import Carriage, Railcar, PassengerCar
from models.train import TrainPassengerCar, Train
from auth import authenticate, authorize

carriage_blueprint = Blueprint('carriage_routes', __name__)

def is_carriage_assigned(session, carriage_id):
    return session.query(
        session.query(Train).filter(Train.railcarID == carriage_id).exists()
    ).scalar()

def serialize_carriage(carriage):
    """Serialize a carriage object based on its type."""
    serialized = {
        "carriageID": carriage.carriageID,
        "trackGauge": carriage.trackGauge,
        "type": carriage.type
    }

    if carriage.type == "Railcar" and carriage.railcar_detail:
        serialized["maxTractiveForce"] = carriage.railcar_detail.maxTractiveForce
    elif carriage.type == "PassengerCar" and carriage.passenger_car_detail:
        serialized.update({
            "numberOfSeats": carriage.passenger_car_detail.numberOfSeats,
            "maxWeight": carriage.passenger_car_detail.maxWeight
        })
    else:
        serialized["message"] = "Invalid carriage type or incomplete data"

    return serialized

@carriage_blueprint.route('/', methods=['GET'])
@authenticate
@authorize(roles=['Employee', 'Admin'])
def get_all_carriages():
    """Retrieve all carriages (Railcars and Passenger Cars)."""
    with SessionLocal() as session:
        carriages = session.query(Carriage).outerjoin(Railcar).outerjoin(PassengerCar).all()
        serialized = [serialize_carriage(c) for c in carriages]
        return jsonify(serialized), 200

@carriage_blueprint.route('/<int:carriage_id>', methods=['GET'])
@authenticate
@authorize(roles=['Employee', 'Admin'])
def get_carriage_by_id(carriage_id):
    """Retrieve a single carriage by ID."""
    with SessionLocal() as session:
        carriage = session.query(Carriage).options(
            joinedload(Carriage.railcar_detail),
            joinedload(Carriage.passenger_car_detail)
        ).filter_by(carriageID=carriage_id).first()

        if not carriage:
            return jsonify({"message": f"Carriage {carriage_id} not found"}), 404

        serialized = serialize_carriage(carriage)
        if "message" in serialized:
            return jsonify(serialized), 400

        return jsonify(serialized), 200

@carriage_blueprint.route('/', methods=['POST'])
@authenticate
@authorize(roles=['Admin'])
def create_carriage():
    """Create a new carriage (Railcar or Passenger Car)."""
    data = request.get_json()
    required_fields = {'trackGauge', 'type'}

    if not data or not required_fields.issubset(data):
        return jsonify({"message": "Missing trackGauge or type"}), 400

    carriage_type = data['type']

    with SessionLocal() as session:
        try:
            carriage = Carriage(trackGauge=data['trackGauge'], type=carriage_type)
            session.add(carriage)
            session.flush()  # Retrieve carriageID before commit

            if carriage_type == "Railcar":
                max_force = data.get('maxTractiveForce')
                if max_force is None:
                    raise ValueError("maxTractiveForce is required for Railcar")
                railcar = Railcar(carriageID=carriage.carriageID, maxTractiveForce=max_force)
                session.add(railcar)
            elif carriage_type == "PassengerCar":
                seats = data.get('numberOfSeats')
                weight = data.get('maxWeight')
                if seats is None or weight is None:
                    raise ValueError("numberOfSeats and maxWeight are required for PassengerCar")
                passenger_car = PassengerCar(
                    carriageID=carriage.carriageID,
                    numberOfSeats=seats,
                    maxWeight=weight
                )
                session.add(passenger_car)
            else:
                raise ValueError("Invalid carriage type")

            session.commit()
            return jsonify({"message": "Carriage created"}), 201
        except (ValueError, IntegrityError) as e:
            session.rollback()
            return jsonify({"message": str(e)}), 400

@carriage_blueprint.route('/<int:carriage_id>', methods=['PUT'])
@authenticate
@authorize(roles=['Admin'])
def update_carriage(carriage_id):
    """Update an existing carriage."""
    data = request.get_json()
    if not data:
        return jsonify({"message": "No data provided for update"}), 400

    with SessionLocal() as session:
        try:
            carriage = session.query(Carriage).options(
                joinedload(Carriage.railcar_detail),
                joinedload(Carriage.passenger_car_detail)
            ).filter_by(carriageID=carriage_id).first()

            if not carriage:
                return jsonify({"message": f"Carriage {carriage_id} not found"}), 404

            if is_carriage_assigned(session, carriage_id):
                return jsonify({"message": "Cannot edit carriage assigned to a train"}), 400

            # Update general fields
            for field in ['trackGauge', 'type']:
                if field in data:
                    setattr(carriage, field, data[field])

            # Update specific details
            if carriage.type == "Railcar" and carriage.railcar_detail:
                if 'maxTractiveForce' in data:
                    carriage.railcar_detail.maxTractiveForce = data['maxTractiveForce']
            elif carriage.type == "PassengerCar" and carriage.passenger_car_detail:
                for field in ['numberOfSeats', 'maxWeight']:
                    if field in data:
                        setattr(carriage.passenger_car_detail, field, data[field])

            session.commit()
            return jsonify({"message": "Carriage updated"}), 200
        except (ValueError, IntegrityError) as e:
            session.rollback()
            return jsonify({"message": str(e)}), 400

@carriage_blueprint.route('/<int:carriage_id>', methods=['DELETE'])
@authenticate
@authorize(roles=['Admin'])
def delete_carriage(carriage_id):
    """Delete a carriage (Railcar or Passenger Car)."""
    with SessionLocal() as session:
        try:
            carriage = session.query(Carriage).options(
                joinedload(Carriage.railcar_detail),
                joinedload(Carriage.passenger_car_detail)
            ).filter_by(carriageID=carriage_id).first()

            if not carriage:
                return jsonify({"message": f"Carriage {carriage_id} not found"}), 404

            if is_carriage_assigned(session, carriage_id):
                return jsonify({"message": "Cannot delete carriage assigned to a train"}), 400

            # Delete specific details
            if carriage.type == "Railcar" and carriage.railcar_detail:
                session.delete(carriage.railcar_detail)
            elif carriage.type == "PassengerCar" and carriage.passenger_car_detail:
                session.delete(carriage.passenger_car_detail)

            session.delete(carriage)
            session.commit()
            return jsonify({"message": "Carriage deleted"}), 200
        except IntegrityError:
            session.rollback()
            return jsonify({"message": "Integrity error"}), 400