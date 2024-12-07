# routes/train_routes.py
from flask import Blueprint, jsonify, request
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload
from database import SessionLocal
from models.train import Train, TrainPassengerCars, TrainType
from models.railcar import Railcar
from models.passenger_car import PassengerCar

train_blueprint = Blueprint('train_routes', __name__)

# Erstellen eines neuen Zuges
@train_blueprint.route('/', methods=['POST'])
def create_train():
    data = request.get_json()

    required_fields = ['name', 'railcarID', 'passengerCarIDs']
    if not data or not all(field in data for field in required_fields):
        return jsonify({"message": f"Fehlende Daten: {', '.join(required_fields)} werden benötigt"}), 400

    name = data['name'].strip()
    railcar_id = data['railcarID']
    passenger_car_ids = data['passengerCarIDs']

    if not passenger_car_ids or not isinstance(passenger_car_ids, list):
        return jsonify({"message": "Es muss mindestens ein PassengerCarID angegeben werden"}), 400

    session = SessionLocal()

    try:
        # Überprüfen, ob der Railcar existiert
        railcar = session.query(Railcar).filter(Railcar.carriageID == railcar_id).first()
        if not railcar:
            return jsonify({"message": f"Railcar mit carriageID {railcar_id} existiert nicht"}), 404

        # Überprüfen, ob der Railcar bereits einem Zug zugeordnet ist
        existing_train = session.query(Train).filter(Train.railcarID == railcar_id).first()
        if existing_train:
            return jsonify({"message": f"Railcar mit carriageID {railcar_id} ist bereits einem Zug zugeordnet"}), 400

        # Überprüfen, ob alle PassengerCars existieren und nicht bereits einem Zug zugeordnet sind (optional)
        passenger_cars = session.query(PassengerCar).filter(PassengerCar.carriageID.in_(passenger_car_ids)).all()
        if len(passenger_cars) != len(passenger_car_ids):
            return jsonify({"message": "Einige PassengerCarIDs existieren nicht"}), 404

        # Optional: Überprüfen, ob PassengerCars bereits einem Zug zugeordnet sind
        # Dies hängt von Ihrer Geschäftslogik ab

        # Erstellen des neuen Zuges
        new_train = Train(
            name=name,
            railcarID=railcar_id
        )
        session.add(new_train)
        session.commit()  # Commit erforderlich, um trainID zu erhalten

        # Hinzufügen der PassengerCars zur Assoziationstabelle
        for pc_id in passenger_car_ids:
            association = TrainPassengerCars(trainID=new_train.trainID, passengerCarID=pc_id)
            session.add(association)

        session.commit()

        # Laden der Beziehungen für die Antwort
        session.refresh(new_train)

        return jsonify({
            'trainID': new_train.trainID,
            'name': new_train.name,
            'railcarID': new_train.railcarID,
            'passengerCarIDs': passenger_car_ids
        }), 201

    except IntegrityError as e:
        session.rollback()
        return jsonify({"message": "Fehler beim Erstellen des Zuges."}), 500
    finally:
        session.close()

# Abrufen aller Züge
@train_blueprint.route('/', methods=['GET'])
def get_trains():
    session = SessionLocal()
    try:
        trains = session.query(Train).options(
            joinedload(Train.railcar),
            joinedload(Train.passenger_cars)
        ).all()

        trains_list = []
        for train in trains:
            passenger_car_ids = [pc.passengerCarID for pc in train.passenger_cars]
            trains_list.append({
                "trainID": train.trainID,
                "name": train.name,
                "railcarID": train.railcarID,
                "passengerCarIDs": passenger_car_ids
            })

        return jsonify(trains_list), 200
    finally:
        session.close()

# Abrufen eines Zuges nach trainID
@train_blueprint.route('/<int:trainID>', methods=['GET'])
def get_train_by_id(trainID):
    session = SessionLocal()
    try:
        train = session.query(Train).options(
            joinedload(Train.railcar),
            joinedload(Train.passenger_cars)
        ).filter(Train.trainID == trainID).first()

        if not train:
            return jsonify({"message": f"Zug mit ID {trainID} nicht gefunden"}), 404

        passenger_car_ids = [pc.passengerCarID for pc in train.passenger_cars]

        return jsonify({
            "trainID": train.trainID,
            "name": train.name,
            "railcarID": train.railcarID,
            "passengerCarIDs": passenger_car_ids
        }), 200
    finally:
        session.close()

# Aktualisieren eines Zuges
@train_blueprint.route('/<int:trainID>', methods=['PUT'])
def update_train(trainID):
    data = request.get_json()
    session = SessionLocal()

    try:
        train = session.query(Train).filter(Train.trainID == trainID).first()

        if not train:
            return jsonify({"message": f"Zug mit ID {trainID} nicht gefunden"}), 404

        # Aktualisieren des Namens
        if 'name' in data:
            name = data['name'].strip()
            if not name:
                return jsonify({"message": "Name darf nicht leer sein"}), 400
            train.name = name

        # Aktualisieren des Railcar
        if 'railcarID' in data:
            new_railcar_id = data['railcarID']
            if new_railcar_id != train.railcarID:
                # Überprüfen, ob der neue Railcar existiert
                new_railcar = session.query(Railcar).filter(Railcar.carriageID == new_railcar_id).first()
                if not new_railcar:
                    return jsonify({"message": f"Railcar mit carriageID {new_railcar_id} existiert nicht"}), 404

                # Überprüfen, ob der neue Railcar bereits einem anderen Zug zugeordnet ist
                existing_train = session.query(Train).filter(Train.railcarID == new_railcar_id).first()
                if existing_train:
                    return jsonify({"message": f"Railcar mit carriageID {new_railcar_id} ist bereits einem Zug zugeordnet"}), 400

                train.railcarID = new_railcar_id

        # Aktualisieren der PassengerCars
        if 'passengerCarIDs' in data:
            new_passenger_car_ids = data['passengerCarIDs']
            if not new_passenger_car_ids or not isinstance(new_passenger_car_ids, list):
                return jsonify({"message": "Es muss mindestens ein PassengerCarID angegeben werden"}), 400

            # Überprüfen, ob alle PassengerCars existieren
            passenger_cars = session.query(PassengerCar).filter(PassengerCar.carriageID.in_(new_passenger_car_ids)).all()
            if len(passenger_cars) != len(new_passenger_car_ids):
                return jsonify({"message": "Einige PassengerCarIDs existieren nicht"}), 404

            # Entfernen bestehender Assoziationen
            session.query(TrainPassengerCars).filter(TrainPassengerCars.trainID == trainID).delete()

            # Hinzufügen neuer Assoziationen
            for pc_id in new_passenger_car_ids:
                association = TrainPassengerCars(trainID=trainID, passengerCarID=pc_id)
                session.add(association)

        session.commit()

        # Laden der aktualisierten Beziehungen
        session.refresh(train)
        updated_passenger_car_ids = [pc.passengerCarID for pc in train.passenger_cars]

        return jsonify({
            "trainID": train.trainID,
            "name": train.name,
            "railcarID": train.railcarID,
            "passengerCarIDs": updated_passenger_car_ids
        }), 200

    except IntegrityError as e:
        session.rollback()
        return jsonify({"message": "Fehler beim Aktualisieren des Zuges."}), 500
    finally:
        session.close()

# Löschen eines Zuges
@train_blueprint.route('/<int:trainID>', methods=['DELETE'])
def delete_train(trainID):
    session = SessionLocal()
    try:
        train = session.query(Train).filter(Train.trainID == trainID).first()

        if not train:
            return jsonify({"message": f"Zug mit ID {trainID} nicht gefunden"}), 404

        session.delete(train)
        session.commit()

        return jsonify({"message": f"Zug mit ID {trainID} wurde erfolgreich gelöscht"}), 200
    except IntegrityError as e:
        session.rollback()
        return jsonify({"message": "Fehler beim Löschen des Zuges."}), 500
    finally:
        session.close()