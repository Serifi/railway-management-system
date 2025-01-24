from flask import Blueprint, request, jsonify
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload
from . import SessionLocal
from models.train import Train, TrainPassengerCar
from models.carriage import Railcar, PassengerCar
from models.maintenance import Maintenance
from auth import authenticate, authorize
from datetime import datetime
from math import fsum

train_blueprint = Blueprint('train_routes', __name__)

def serialize_train(train):
    """Serialize a Train including its Railcar and associated PassengerCars."""
    railcar_data = None
    if train.railcar:
        railcar_data = {
            "carriageID": train.railcar.carriageID,
            "trackGauge": train.railcar.carriage.trackGauge,
            "maxTractiveForce": train.railcar.maxTractiveForce
        }

    passenger_cars = [
        {
            "carriageID": assoc.passenger_car.carriageID,
            "trackGauge": assoc.passenger_car.carriage.trackGauge,
            "numberOfSeats": assoc.passenger_car.numberOfSeats,
            "maxWeight": assoc.passenger_car.maxWeight,
            "position": assoc.position
        }
        for assoc in train.passenger_cars_associations
    ]

    # Determine if the train is active (no ongoing maintenance)
    now = datetime.utcnow()
    active = not any(
        m.from_time <= now <= m.to_time for m in train.maintenances
    )

    return {
        "trainID": train.trainID,
        "name": train.name,
        "railcar": railcar_data,
        "passenger_cars": passenger_cars,
        "active": active
    }


def validate_track_gauge(railcar, passenger_cars):
    """Ensure all carriages in the train have the same trackGauge."""
    railcar_gauge = railcar.carriage.trackGauge
    for pc in passenger_cars:
        if pc.carriage.trackGauge != railcar_gauge:
            return False
    return True


def calculate_total_weight(passenger_cars):
    """Calculate the total maxWeight of all passenger cars."""
    return fsum(pc.maxWeight for pc in passenger_cars)


def is_railcar_assigned(session, railcar_id, current_train_id=None):
    """ Check if the railcar is already assigned to another train. """
    query = session.query(Train).filter_by(railcarID=railcar_id)
    if current_train_id:
        query = query.filter(Train.trainID != current_train_id)
    existing_train = query.first()
    return existing_train is not None


def is_passenger_car_assigned(session, passenger_car_id, current_train_id=None):
    """ Check if the passenger car is already assigned to another train. """
    query = session.query(TrainPassengerCar).filter_by(passengerCarID=passenger_car_id)
    if current_train_id:
        query = query.filter(TrainPassengerCar.trainID != current_train_id)
    existing_assoc = query.first()
    return existing_assoc is not None


@train_blueprint.route('/', methods=['GET'])
# @authenticate       Für Integration mit schedule
# @authorize(roles=['Employee', 'Admin'])
def get_trains():
    """Retrieve all trains."""
    with SessionLocal() as session:
        trains = session.query(Train).options(
            joinedload(Train.railcar).joinedload(Railcar.carriage),
            joinedload(Train.passenger_cars_associations).joinedload(TrainPassengerCar.passenger_car).joinedload(PassengerCar.carriage),
            joinedload(Train.maintenances)
        ).all()
        serialized_trains = [serialize_train(train) for train in trains]
        return jsonify(serialized_trains), 200


@train_blueprint.route('/<int:train_id>', methods=['GET'])
# @authenticate       Für Integration mit schedule
# @authorize(roles=['Employee', 'Admin'])
def get_train_by_id(train_id):
    """Retrieve a specific train by ID."""
    with SessionLocal() as session:
        train = session.query(Train).options(
            joinedload(Train.railcar).joinedload(Railcar.carriage),
            joinedload(Train.passenger_cars_associations).joinedload(TrainPassengerCar.passenger_car).joinedload(PassengerCar.carriage),
            joinedload(Train.maintenances)
        ).filter_by(trainID=train_id).first()

        if not train:
            return jsonify({"message": f"Train {train_id} not found"}), 404

        serialized_train = serialize_train(train)
        return jsonify(serialized_train), 200


@train_blueprint.route('/', methods=['POST'])
@authenticate
@authorize(roles=['Admin'])
def create_train():
    """Create a new train, ensuring all carriages have the same trackGauge and weight constraints are met."""
    data = request.get_json()
    required_fields = {'name', 'railcarID'}

    if not data or not required_fields.issubset(data):
        missing = required_fields - data.keys()
        return jsonify({"message": f"Missing required fields: {', '.join(missing)}"}), 400

    name = data['name'].strip()
    railcar_id = data['railcarID']
    passenger_cars_data = data.get('passenger_cars', [])

    with SessionLocal() as session:
        try:
            # Validate the chosen Railcar
            railcar = session.query(Railcar).filter_by(carriageID=railcar_id).first()
            if not railcar:
                return jsonify({"message": f"Railcar {railcar_id} not found"}), 404

            # Ensure the Railcar is not already in use
            if is_railcar_assigned(session, railcar_id):
                existing_train = session.query(Train).filter_by(railcarID=railcar_id).first()
                return jsonify({"message": f"Railcar {railcar_id} is already assigned to Train {existing_train.trainID}"}), 400

            # Initialize the Train
            train = Train(name=name, railcarID=railcar_id)
            session.add(train)
            session.flush()  # Flush to assign trainID

            if passenger_cars_data:
                # Extract PassengerCar IDs
                pc_ids = [item['carriageID'] for item in passenger_cars_data]

                # Check if any PassengerCar is already assigned
                for pc_id in pc_ids:
                    if is_passenger_car_assigned(session, pc_id):
                        existing_assoc = session.query(TrainPassengerCar).filter_by(passengerCarID=pc_id).first()
                        return jsonify({"message": f"PassengerCar {pc_id} is already assigned to Train {existing_assoc.trainID}"}), 400

                # Fetch PassengerCar objects
                passenger_cars = session.query(PassengerCar).filter(PassengerCar.carriageID.in_(pc_ids)).all()

                if len(passenger_cars) != len(pc_ids):
                    return jsonify({"message": "Some PassengerCar IDs are invalid"}), 404

                # Check trackGauge consistency
                if not validate_track_gauge(railcar, passenger_cars):
                    return jsonify({"message": "All carriages must have the same trackGauge"}), 400

                # Check tractive force
                total_weight = calculate_total_weight(passenger_cars)
                if total_weight > railcar.maxTractiveForce:
                    return jsonify({"message": "Railcar's max tractive force exceeded by passenger cars' total weight"}), 400

                # Create associations
                for pc_data in passenger_cars_data:
                    position = pc_data.get('position', 1)
                    assoc = TrainPassengerCar(
                        trainID=train.trainID,
                        passengerCarID=pc_data['carriageID'],
                        position=position
                    )
                    session.add(assoc)

            session.commit()
            return jsonify({"message": "Train created successfully", "trainID": train.trainID}), 201

        except IntegrityError as ie:
            session.rollback()
            return jsonify({"message": "Integrity error occurred while creating the train", "details": str(ie.orig)}), 400
        except Exception as e:
            session.rollback()
            return jsonify({"message": "An error occurred", "details": str(e)}), 500


@train_blueprint.route('/<int:train_id>', methods=['PUT'])
@authenticate
@authorize(roles=['Admin'])
def update_train(train_id):
    """Update an existing train, ensuring trackGauge consistency and weight constraints when railcar or passenger cars change."""
    data = request.get_json()
    if not data:
        return jsonify({"message": "No data provided for update"}), 400

    with SessionLocal() as session:
        try:
            train = session.query(Train).options(
                joinedload(Train.railcar).joinedload(Railcar.carriage),
                joinedload(Train.passenger_cars_associations).joinedload(TrainPassengerCar.passenger_car).joinedload(PassengerCar.carriage)
            ).filter_by(trainID=train_id).first()

            if not train:
                return jsonify({"message": f"Train {train_id} not found"}), 404

            # Update name if provided
            if 'name' in data:
                train.name = data['name'].strip()

            # Handle railcar update
            if 'railcarID' in data and data['railcarID'] != train.railcarID:
                new_railcar_id = data['railcarID']
                new_railcar = session.query(Railcar).filter_by(carriageID=new_railcar_id).first()
                if not new_railcar:
                    return jsonify({"message": f"Railcar {new_railcar_id} not found"}), 404

                # Check if the new railcar is already assigned to another train
                if is_railcar_assigned(session, new_railcar_id, current_train_id=train_id):
                    existing_train = session.query(Train).filter_by(railcarID=new_railcar_id).first()
                    return jsonify({"message": f"Railcar {new_railcar_id} is already assigned to Train {existing_train.trainID}"}), 400

                # Validate trackGauge consistency with existing passenger cars
                passenger_cars = [assoc.passenger_car for assoc in train.passenger_cars_associations]
                if not validate_track_gauge(new_railcar, passenger_cars):
                    return jsonify({"message": "Track gauge mismatch with existing passenger cars"}), 400

                # Validate tractive force with existing passenger cars
                total_weight = calculate_total_weight(passenger_cars)
                if total_weight > new_railcar.maxTractiveForce:
                    return jsonify({"message": "New railcar's max tractive force is exceeded by passenger cars' total weight"}), 400

                # Update railcarID
                train.railcarID = new_railcar_id

            # Handle passenger cars update
            if 'passenger_cars' in data:
                passenger_cars_data = data['passenger_cars']
                pc_ids = [pc_data['carriageID'] for pc_data in passenger_cars_data]

                # Check if any PassengerCar is already assigned to another train
                for pc_id in pc_ids:
                    if is_passenger_car_assigned(session, pc_id, current_train_id=train_id):
                        existing_assoc = session.query(TrainPassengerCar).filter_by(passengerCarID=pc_id).first()
                        return jsonify({"message": f"PassengerCar {pc_id} is already assigned to Train {existing_assoc.trainID}"}), 400

                # Fetch PassengerCar objects
                passenger_cars = session.query(PassengerCar).filter(PassengerCar.carriageID.in_(pc_ids)).all()

                if len(passenger_cars) != len(pc_ids):
                    return jsonify({"message": "Some PassengerCar IDs are invalid"}), 404

                # Fetch current railcar to check trackGauge
                railcar = session.query(Railcar).filter_by(carriageID=train.railcarID).first()
                if not railcar:
                    return jsonify({"message": f"Railcar {train.railcarID} not found"}), 404

                # Check trackGauge consistency
                if not validate_track_gauge(railcar, passenger_cars):
                    return jsonify({"message": "All carriages must have the same trackGauge"}), 400

                # Check tractive force
                total_weight = calculate_total_weight(passenger_cars)
                if total_weight > railcar.maxTractiveForce:
                    return jsonify({"message": "Railcar's max tractive force exceeded by passenger cars' total weight"}), 400

                # Remove existing associations
                session.query(TrainPassengerCar).filter_by(trainID=train_id).delete()

                # Create new associations
                for pc_data in passenger_cars_data:
                    position = pc_data.get('position', 1)
                    assoc = TrainPassengerCar(
                        trainID=train_id,
                        passengerCarID=pc_data['carriageID'],
                        position=position
                    )
                    session.add(assoc)

            session.commit()
            return jsonify({"message": "Train updated successfully"}), 200

        except IntegrityError as ie:
            session.rollback()
            return jsonify({"message": "Integrity error occurred while updating the train", "details": str(ie.orig)}), 400
        except Exception as e:
            session.rollback()
            return jsonify({"message": "An error occurred", "details": str(e)}), 500


@train_blueprint.route('/<int:train_id>', methods=['DELETE'])
@authenticate
@authorize(roles=['Admin'])
def delete_train(train_id):
    """Delete a train, disallowing deletion if it has ongoing or upcoming maintenance records."""
    with SessionLocal() as session:
        try:
            # Fetch the train
            train = session.query(Train).filter_by(trainID=train_id).first()
            if not train:
                return jsonify({"message": f"Train with ID {train_id} not found"}), 404

            # Check if the train has ongoing or upcoming maintenance
            from datetime import datetime
            now = datetime.utcnow()
            maintenance_exists = session.query(Maintenance).filter(
                Maintenance.trainID == train_id,
                Maintenance.to_time >= now
            ).first()

            if maintenance_exists:
                return jsonify({"message": "Cannot delete train with ongoing or upcoming maintenance records"}), 400

            # Delete the train
            session.delete(train)
            session.commit()
            return jsonify({"message": f"Train with ID {train_id} deleted successfully"}), 200

        except IntegrityError as ie:
            session.rollback()
            return jsonify({"message": "An integrity error occurred while deleting the train", "details": str(ie.orig)}), 400
        except Exception as e:
            session.rollback()
            return jsonify({"message": "An unexpected error occurred", "details": str(e)}), 500
