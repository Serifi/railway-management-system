from sqlalchemy.exc import IntegrityError  # Korrigierter Import
from flask import Blueprint, request, jsonify
from sqlalchemy.orm import sessionmaker, joinedload
from models import Base, Train, TrainPassengerCars
from models.carriage import Railcar, PassengerCar
from sqlalchemy import create_engine
import os

# Blueprint für Train-Routen
train_blueprint = Blueprint('train_routes', __name__)

# Datenbank-URL und Engine
DATABASE_URL = f"sqlite:///{os.path.abspath('server/db/fleet.db')}"
engine = create_engine(DATABASE_URL, echo=True)
Session = sessionmaker(bind=engine)

# Stelle sicher, dass alle Modelle importiert werden
import models

# Erstelle Tabellen (falls noch nicht vorhanden)
Base.metadata.create_all(engine)

# POST-Route zum Erstellen eines neuen Zuges
@train_blueprint.route('/', methods=['POST'])
def create_train():
    session = Session()
    try:
        data = request.get_json()

        # Validierung der Eingabedaten
        if not data or 'name' not in data or 'railcarID' not in data or 'passengerCarIDs' not in data:
            return jsonify({"message": "Name, railcarID und passengerCarIDs sind erforderlich"}), 400

        # Railcar überprüfen
        railcar = session.query(Railcar).filter_by(carriageID=data['railcarID']).first()
        if not railcar:
            return jsonify({"message": "Ungültige railcarID"}), 404

        # Prüfen, ob Railcar bereits einem anderen Zug zugeordnet ist
        existing_train = session.query(Train).filter(Train.railcarID == data['railcarID']).first()
        if existing_train:
            return jsonify({"message": "Dieser Railcar ist bereits einem Zug zugeordnet"}), 400

        # PassengerCars überprüfen
        passenger_car_ids = data['passengerCarIDs']
        if not passenger_car_ids:
            return jsonify({"message": "Es muss mindestens ein PassengerCarID angegeben werden"}), 400

        passenger_cars = session.query(PassengerCar).filter(PassengerCar.carriageID.in_(passenger_car_ids)).all()
        if len(passenger_cars) != len(passenger_car_ids):
            return jsonify({"message": "Einige PassengerCar-IDs sind ungültig"}), 404

        # Train erstellen
        new_train = Train(name=data['name'], railcarID=data['railcarID'])
        session.add(new_train)
        session.commit()

        # Verknüpfungen in der Zwischentabelle hinzufügen
        for pc in passenger_cars:
            session.execute(
                TrainPassengerCars.insert().values(trainID=new_train.trainID, passengerCarID=pc.carriageID)
            )
        session.commit()

        return jsonify({
            "trainID": new_train.trainID,
            "name": new_train.name,
            "railcarID": new_train.railcarID,
            "passengerCarIDs": passenger_car_ids
        }), 201

    except IntegrityError:
        session.rollback()
        return jsonify({"message": "Datenbankfehler: Duplizierte oder ungültige Daten"}), 400
    finally:
        session.close()

# GET-Route zum Abrufen aller Züge
@train_blueprint.route('/', methods=['GET'])
def get_trains():
    session = Session()
    try:
        trains = session.query(Train).options(
            joinedload(Train.railcar),
            joinedload(Train.passenger_cars)
        ).all()

        trains_list = []
        for train in trains:
            passenger_car_ids = [pc.carriageID for pc in train.passenger_cars]
            trains_list.append({
                "trainID": train.trainID,
                "name": train.name,
                "railcarID": train.railcarID,
                "passengerCarIDs": passenger_car_ids
            })

        return jsonify(trains_list), 200
    finally:
        session.close()

# GET-Route zum Abrufen eines Zuges nach trainID
@train_blueprint.route('/<int:trainID>', methods=['GET'])
def get_train_by_id(trainID):
    session = Session()
    try:
        train = session.query(Train).options(
            joinedload(Train.railcar),
            joinedload(Train.passenger_cars)
        ).filter(Train.trainID == trainID).first()

        if not train:
            return jsonify({"message": f"Zug mit ID {trainID} nicht gefunden"}), 404

        passenger_car_ids = [pc.carriageID for pc in train.passenger_cars]

        return jsonify({
            "trainID": train.trainID,
            "name": train.name,
            "railcarID": train.railcarID,
            "passengerCarIDs": passenger_car_ids
        }), 200
    finally:
        session.close()

# PUT-Route zum Aktualisieren eines Zuges
@train_blueprint.route('/<int:trainID>', methods=['PUT'])
def update_train(trainID):
    data = request.get_json()
    session = Session()

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
            session.query(TrainPassengerCars).filter(TrainPassengerCars.c.trainID == trainID).delete()

            # Hinzufügen neuer Assoziationen
            for pc in passenger_cars:
                session.execute(
                    TrainPassengerCars.insert().values(trainID=trainID, passengerCarID=pc.carriageID)
                )
        session.commit()

        # Laden der aktualisierten Beziehungen
        session.refresh(train)
        updated_passenger_car_ids = [pc.carriageID for pc in train.passenger_cars]

        return jsonify({
            "trainID": train.trainID,
            "name": train.name,
            "railcarID": train.railcarID,
            "passengerCarIDs": updated_passenger_car_ids
        }), 200

    except IntegrityError:
        session.rollback()
        return jsonify({"message": "Fehler beim Aktualisieren des Zuges."}), 500
    finally:
        session.close()

# DELETE-Route zum Löschen eines Zuges
@train_blueprint.route('/<int:trainID>', methods=['DELETE'])
def delete_train(trainID):
    session = Session()
    try:
        train = session.query(Train).filter(Train.trainID == trainID).first()

        if not train:
            return jsonify({"message": f"Zug mit ID {trainID} nicht gefunden"}), 404

        session.delete(train)
        session.commit()

        return jsonify({"message": f"Zug mit ID {trainID} wurde erfolgreich gelöscht"}), 200
    except IntegrityError:
        session.rollback()
        return jsonify({"message": "Fehler beim Löschen des Zuges."}), 500
    finally:
        session.close()
