# server/routes/maintenance_routes.py

from flask import Blueprint, request, jsonify
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker
from models import Maintenance, Employee, Train
from models import Base
from sqlalchemy import create_engine
import os
from datetime import datetime

maintenance_blueprint = Blueprint('maintenance_routes', __name__)

DATABASE_URL = f"sqlite:///{os.path.abspath('server/db/fleet.db')}"
engine = create_engine(DATABASE_URL, echo=True)
Session = sessionmaker(bind=engine)

import models

Base.metadata.create_all(engine)

@maintenance_blueprint.route('/', methods=['POST'])
def create_maintenance():
    session = Session()
    try:
        data = request.get_json()

        # Validierung der Eingabedaten
        required_fields = ['employeeSSN', 'trainID', 'from_time', 'to_time']
        if not data or not all(field in data for field in required_fields):
            return jsonify({"message": "employeeSSN, trainID, from_time und to_time sind erforderlich"}), 400

        employee_ssn = data['employeeSSN']
        train_id = data['trainID']
        from_time_str = data['from_time']
        to_time_str = data['to_time']

        # Parse Timestamps
        try:
            from_time = datetime.fromisoformat(from_time_str)
            to_time = datetime.fromisoformat(to_time_str)
        except ValueError:
            return jsonify({"message": "Ungültiges Datumsformat. Verwende ISO-Format (YYYY-MM-DDTHH:MM:SS)."}), 400

        if from_time >= to_time:
            return jsonify({"message": "'from_time' muss vor 'to_time' liegen"}), 400

        # Überprüfen, ob Employee existiert
        employee = session.query(Employee).filter_by(ssn=employee_ssn).first()
        if not employee:
            return jsonify({"message": f"Mitarbeiter mit SSN {employee_ssn} existiert nicht"}), 404

        # Überprüfen, ob Train existiert
        train = session.query(Train).filter_by(trainID=train_id).first()
        if not train:
            return jsonify({"message": f"Zug mit ID {train_id} existiert nicht"}), 404

        # Optional: Überprüfen, ob der Employee bereits eine Wartung zur selben Zeit hat
        overlapping_maintenance = session.query(Maintenance).filter(
            Maintenance.employeeSSN == employee_ssn,
            Maintenance.from_time <= to_time,
            Maintenance.to_time >= from_time
        ).first()
        if overlapping_maintenance:
            return jsonify({"message": "Der Mitarbeiter hat bereits eine Wartung zu diesem Zeitpunkt"}), 400

        # Wartung erstellen
        new_maintenance = Maintenance(
            employeeSSN=employee_ssn,
            trainID=train_id,
            from_time=from_time,
            to_time=to_time
        )

        session.add(new_maintenance)
        session.commit()

        return jsonify({
            "maintenanceID": new_maintenance.maintenanceID,
            "employeeSSN": new_maintenance.employeeSSN,
            "trainID": new_maintenance.trainID,
            "from_time": new_maintenance.from_time.isoformat(),
            "to_time": new_maintenance.to_time.isoformat()
        }), 201

    except IntegrityError:
        session.rollback()
        return jsonify({"message": "Datenbankfehler: Duplizierte oder ungültige Daten"}), 400
    except Exception as e:
        session.rollback()
        return jsonify({"message": f"Fehler: {str(e)}"}), 500
    finally:
        session.close()

# Optional: GET-Route zum Abrufen aller Wartungen
@maintenance_blueprint.route('/', methods=['GET'])
def get_maintenances():
    session = Session()
    try:
        maintenances = session.query(Maintenance).all()

        maintenances_list = [
            {
                "maintenanceID": m.maintenanceID,
                "employeeSSN": m.employeeSSN,
                "trainID": m.trainID,
                "from_time": m.from_time.isoformat(),
                "to_time": m.to_time.isoformat()
            }
            for m in maintenances
        ]

        return jsonify(maintenances_list), 200
    finally:
        session.close()

# Optional: GET-Route zum Abrufen einer Wartung nach maintenanceID
@maintenance_blueprint.route('/<int:maintenanceID>', methods=['GET'])
def get_maintenance_by_id(maintenanceID):
    session = Session()
    try:
        maintenance = session.query(Maintenance).filter(Maintenance.maintenanceID == maintenanceID).first()

        if not maintenance:
            return jsonify({"message": f"Wartung mit ID {maintenanceID} nicht gefunden"}), 404

        return jsonify({
            "maintenanceID": maintenance.maintenanceID,
            "employeeSSN": maintenance.employeeSSN,
            "trainID": maintenance.trainID,
            "from_time": maintenance.from_time.isoformat(),
            "to_time": maintenance.to_time.isoformat()
        }), 200
    finally:
        session.close()

# Optional: PUT-Route zum Aktualisieren einer Wartung
@maintenance_blueprint.route('/<int:maintenanceID>', methods=['PUT'])
def update_maintenance(maintenanceID):
    session = Session()
    try:
        maintenance = session.query(Maintenance).filter(Maintenance.maintenanceID == maintenanceID).first()

        if not maintenance:
            return jsonify({"message": f"Wartung mit ID {maintenanceID} nicht gefunden"}), 404

        data = request.get_json()

        if 'employeeSSN' in data:
            employee_ssn = data['employeeSSN']
            employee = session.query(Employee).filter_by(ssn=employee_ssn).first()
            if not employee:
                return jsonify({"message": f"Mitarbeiter mit SSN {employee_ssn} existiert nicht"}), 404
            maintenance.employeeSSN = employee_ssn

        if 'trainID' in data:
            train_id = data['trainID']
            train = session.query(Train).filter_by(trainID=train_id).first()
            if not train:
                return jsonify({"message": f"Zug mit ID {train_id} existiert nicht"}), 404
            maintenance.trainID = train_id

        if 'from_time' in data:
            try:
                from_time = datetime.fromisoformat(data['from_time'])
                maintenance.from_time = from_time
            except ValueError:
                return jsonify({"message": "Ungültiges Datumsformat für 'from_time'. Verwende ISO-Format (YYYY-MM-DDTHH:MM:SS)."}), 400

        if 'to_time' in data:
            try:
                to_time = datetime.fromisoformat(data['to_time'])
                maintenance.to_time = to_time
            except ValueError:
                return jsonify({"message": "Ungültiges Datumsformat für 'to_time'. Verwende ISO-Format (YYYY-MM-DDTHH:MM:SS)."}), 400

        if maintenance.from_time >= maintenance.to_time:
            return jsonify({"message": "'from_time' muss vor 'to_time' liegen"}), 400

        # Optional: Überprüfen von Überlappungen wie beim Erstellen

        session.commit()

        return jsonify({
            "maintenanceID": maintenance.maintenanceID,
            "employeeSSN": maintenance.employeeSSN,
            "trainID": maintenance.trainID,
            "from_time": maintenance.from_time.isoformat(),
            "to_time": maintenance.to_time.isoformat()
        }), 200

    except IntegrityError:
        session.rollback()
        return jsonify({"message": "Datenbankfehler: Duplizierte oder ungültige Daten"}), 400
    except Exception as e:
        session.rollback()
        return jsonify({"message": f"Fehler: {str(e)}"}), 500
    finally:
        session.close()

# Optional: DELETE-Route zum Löschen einer Wartung
@maintenance_blueprint.route('/<int:maintenanceID>', methods=['DELETE'])
def delete_maintenance(maintenanceID):
    session = Session()
    try:
        maintenance = session.query(Maintenance).filter(Maintenance.maintenanceID == maintenanceID).first()

        if not maintenance:
            return jsonify({"message": f"Wartung mit ID {maintenanceID} nicht gefunden"}), 404

        session.delete(maintenance)
        session.commit()

        return jsonify({"message": f"Wartung mit ID {maintenanceID} wurde erfolgreich gelöscht"}), 200
    except IntegrityError:
        session.rollback()
        return jsonify({"message": "Datenbankfehler: Fehler beim Löschen der Wartung."}), 400
    finally:
        session.close()