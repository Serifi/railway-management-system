from flask import Blueprint, request, jsonify
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload
from . import SessionLocal
from models.carriage import Carriage, Railcar, PassengerCar
from models.train import TrainPassengerCar, Train
from auth import authenticate, authorize

carriage_blueprint = Blueprint('carriage_routes', __name__)

def is_carriage_assigned(session, carriage_id):
    """ Check if a carriage is already assigned to a train """
    return session.query(
        session.query(Train).filter(Train.railcarID == carriage_id).exists()
    ).scalar()

def serialize_carriage(carriage):
    """ Serialize a carriage object based on its type """
    serialized = {
        "carriageID": carriage.carriageID,
        "trackGauge": carriage.trackGauge,
        "type": carriage.type
    }

    # Details based on carriage type
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
    """ Retrieve all carriages """
    with SessionLocal() as session:
        carriages = session.query(Carriage).outerjoin(Railcar).outerjoin(PassengerCar).all()
        serialized = [serialize_carriage(c) for c in carriages]
        return jsonify(serialized), 200

@carriage_blueprint.route('/<int:carriage_id>', methods=['GET'])
@authenticate
@authorize(roles=['Employee', 'Admin'])
def get_carriage_by_id(carriage_id):
    """ Retrieve a single carriage by ID """
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
    """ Create a new carriage """
    data = request.get_json()
    required_fields = {'trackGauge', 'type'}

    if not data or not required_fields.issubset(data):
        return jsonify({"message": "Missing trackGauge or type"}), 400

    carriage_type = data['type']

    with SessionLocal() as session:
        try:
            # Create the base Carriage
            carriage = Carriage(trackGauge=data['trackGauge'], type=carriage_type)
            session.add(carriage)
            session.flush()

            # Handle type-specific creation
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
            return jsonify({"message": f"Carriage with ID #{carriage.carriageID} is now available"}), 201
        except (ValueError, IntegrityError) as e:
            session.rollback()
            return jsonify({"message": str(e)}), 400


@carriage_blueprint.route('/<int:carriage_id>', methods=['PUT'])
@authenticate
@authorize(roles=['Admin'])
def update_carriage(carriage_id):
    """ Update an existing carriage and switch type if necessary. """
    data = request.get_json()
    if not data:
        return jsonify({"message": "No data provided for update"}), 400

    with SessionLocal() as session:
        try:
            # Load the carriage with any type-specific attributes
            carriage = session.query(Carriage).options(
                joinedload(Carriage.railcar_detail),
                joinedload(Carriage.passenger_car_detail)
            ).filter_by(carriageID=carriage_id).first()

            if not carriage:
                return jsonify({"message": f"Carriage #{carriage_id} not found"}), 404

            # Prevent updates if the carriage is assigned to a train
            if is_carriage_assigned(session, carriage_id):
                return jsonify({"message": f"Cannot edit carriage #{carriage_id} assigned to a train"}), 400

            old_type = carriage.type

            # Update general carriage fields, if given
            if 'trackGauge' in data:
                carriage.trackGauge = data['trackGauge']
            if 'type' in data:
                carriage.type = data['type']

            new_type = carriage.type

            # If the type changed, remove old type-specific row, then insert the new one
            if old_type != new_type:
                # Delete the old type-specific row, if any ---
                if carriage.railcar_detail:
                    session.delete(carriage.railcar_detail)
                if carriage.passenger_car_detail:
                    session.delete(carriage.passenger_car_detail)

                session.flush()

                # Insert the new type-specific row
                if new_type == "Railcar":
                    if 'maxTractiveForce' not in data:
                        raise ValueError("maxTractiveForce is required for a Railcar.")
                    new_railcar = Railcar(
                        carriageID=carriage.carriageID,
                        maxTractiveForce=data['maxTractiveForce']
                    )
                    session.add(new_railcar)

                elif new_type == "PassengerCar":
                    # Check required fields
                    if 'numberOfSeats' not in data or 'maxWeight' not in data:
                        raise ValueError("numberOfSeats and maxWeight are required for a PassengerCar.")
                    new_passenger_car = PassengerCar(
                        carriageID=carriage.carriageID,
                        numberOfSeats=data['numberOfSeats'],
                        maxWeight=data['maxWeight']
                    )
                    session.add(new_passenger_car)

            else:
                # If type has not changed, just update the existing row, if it exists
                if new_type == "Railcar":
                    if carriage.railcar_detail and 'maxTractiveForce' in data:
                        carriage.railcar_detail.maxTractiveForce = data['maxTractiveForce']
                    elif not carriage.railcar_detail:
                        # If it's missing, create a new railcar entry
                        if 'maxTractiveForce' not in data:
                            raise ValueError("maxTractiveForce is required to create a missing Railcar entry.")
                        session.add(Railcar(
                            carriageID=carriage.carriageID,
                            maxTractiveForce=data['maxTractiveForce']
                        ))

                elif new_type == "PassengerCar":
                    if carriage.passenger_car_detail:
                        if 'numberOfSeats' in data:
                            carriage.passenger_car_detail.numberOfSeats = data['numberOfSeats']
                        if 'maxWeight' in data:
                            carriage.passenger_car_detail.maxWeight = data['maxWeight']
                    else:
                        # If it's missing, create a new passenger_car entry
                        if 'numberOfSeats' not in data or 'maxWeight' not in data:
                            raise ValueError("numberOfSeats and maxWeight are required to create a missing PassengerCar entry.")
                        session.add(PassengerCar(
                            carriageID=carriage.carriageID,
                            numberOfSeats=data['numberOfSeats'],
                            maxWeight=data['maxWeight']
                        ))

            session.commit()
            return jsonify({"message": f"Carriage with ID #{carriage.carriageID} is updated"}), 200

        except (ValueError, IntegrityError) as e:
            session.rollback()
            return jsonify({"message": str(e)}), 400


@carriage_blueprint.route('/<int:carriage_id>', methods=['DELETE'])
@authenticate
@authorize(roles=['Admin'])
def delete_carriage(carriage_id):
    """Delete a carriage"""
    with SessionLocal() as session:
        try:
            carriage = session.query(Carriage).options(
                joinedload(Carriage.railcar_detail),
                joinedload(Carriage.passenger_car_detail)
            ).filter_by(carriageID=carriage_id).first()

            if not carriage:
                return jsonify({"message": f"Carriage {carriage_id} not found"}), 404

            # Prevent deletion if the carriage is assigned to a train
            if is_carriage_assigned(session, carriage_id):
                return jsonify({"message": f"Cannot delete carriage {carriage_id} assigned to a train"}), 400

            # Delete type-specific details
            if carriage.type == "Railcar" and carriage.railcar_detail:
                session.delete(carriage.railcar_detail)
            elif carriage.type == "PassengerCar" and carriage.passenger_car_detail:
                session.delete(carriage.passenger_car_detail)

            # Delete general fields
            session.delete(carriage)
            session.commit()
            return jsonify({"message": f"Carriage with ID #{carriage.carriageID} is now deleted"}), 200
        except IntegrityError:
            session.rollback()
            return jsonify({"message": "Integrity error"}), 400