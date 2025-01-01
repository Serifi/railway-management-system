import os
from flask import Blueprint, request, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from models import Base, Maintenance, Employee, Train

maintenance_blueprint = Blueprint('maintenance_blueprint', __name__)

DATABASE_URL = f"sqlite:///{os.path.abspath('server/db/fleet.db')}"
engine = create_engine(DATABASE_URL, echo=False)
Session = sessionmaker(bind=engine)
Base.metadata.create_all(engine)

@maintenance_blueprint.route('/', methods=['POST'])
def create_maintenance():
    session = Session()
    try:
        data = request.get_json()
        for f in ['employeeSSN', 'trainID', 'from_time', 'to_time']:
            if f not in data:
                return jsonify({"message": f"{f} required"}), 400

        emp = session.query(Employee).filter_by(ssn=data['employeeSSN']).first()
        if not emp:
            return jsonify({"message": "Employee not found"}), 404

        train = session.query(Train).filter_by(trainID=data['trainID']).first()
        if not train:
            return jsonify({"message": "Train not found"}), 404

        from_t = datetime.fromisoformat(data['from_time'])
        to_t = datetime.fromisoformat(data['to_time'])
        if from_t >= to_t:
            return jsonify({"message": "from_time must be < to_time"}), 400

        # Overlap check for this employee
        overlap = session.query(Maintenance).filter(
            Maintenance.employeeSSN == data['employeeSSN'],
            Maintenance.from_time < to_t,
            Maintenance.to_time > from_t
        ).first()
        if overlap:
            return jsonify({"message": "Employee already assigned in overlapping time"}), 400

        m = Maintenance(employeeSSN=emp.ssn, trainID=train.trainID, from_time=from_t, to_time=to_t)
        session.add(m)
        session.commit()
        return jsonify({"message": "Maintenance created"}), 201
    except IntegrityError:
        session.rollback()
        return jsonify({"message": "DB error"}), 400
    except ValueError:
        return jsonify({"message": "Invalid date format"}), 400
    finally:
        session.close()

@maintenance_blueprint.route('/', methods=['GET'])
def get_maintenances():
    session = Session()
    try:
        ms = session.query(Maintenance).all()
        out = []
        for i in ms:
            out.append({
                "maintenanceID": i.maintenanceID,
                "employeeSSN": i.employeeSSN,
                "trainID": i.trainID,
                "from_time": i.from_time.isoformat(),
                "to_time": i.to_time.isoformat()
            })
        return jsonify(out), 200
    finally:
        session.close()

@maintenance_blueprint.route('/<int:maintenanceID>', methods=['GET'])
def get_maintenance_by_id(maintenanceID):
    session = Session()
    try:
        m = session.query(Maintenance).filter_by(maintenanceID=maintenanceID).first()
        if not m:
            return jsonify({"message": "Maintenance not found"}), 404
        return jsonify({
            "maintenanceID": m.maintenanceID,
            "employeeSSN": m.employeeSSN,
            "trainID": m.trainID,
            "from_time": m.from_time.isoformat(),
            "to_time": m.to_time.isoformat()
        }), 200
    finally:
        session.close()

@maintenance_blueprint.route('/<int:maintenanceID>', methods=['PUT'])
def update_maintenance(maintenanceID):
    session = Session()
    try:
        data = request.get_json()
        m = session.query(Maintenance).filter_by(maintenanceID=maintenanceID).first()
        if not m:
            return jsonify({"message": "Maintenance not found"}), 404

        if 'employeeSSN' in data:
            e = session.query(Employee).filter_by(ssn=data['employeeSSN']).first()
            if not e:
                return jsonify({"message": "Employee not found"}), 404
            m.employeeSSN = e.ssn

        if 'trainID' in data:
            t = session.query(Train).filter_by(trainID=data['trainID']).first()
            if not t:
                return jsonify({"message": "Train not found"}), 404
            m.trainID = t.trainID

        if 'from_time' in data:
            m.from_time = datetime.fromisoformat(data['from_time'])
        if 'to_time' in data:
            m.to_time = datetime.fromisoformat(data['to_time'])
        if m.from_time >= m.to_time:
            return jsonify({"message": "from_time must be < to_time"}), 400

        # Overlap check again
        overlap = session.query(Maintenance).filter(
            Maintenance.maintenanceID != maintenanceID,
            Maintenance.employeeSSN == m.employeeSSN,
            Maintenance.from_time < m.to_time,
            Maintenance.to_time > m.from_time
        ).first()
        if overlap:
            return jsonify({"message": "Employee overlap"}), 400

        session.commit()
        return jsonify({"message": "Maintenance updated"}), 200
    except IntegrityError:
        session.rollback()
        return jsonify({"message": "DB error"}), 400
    except ValueError:
        return jsonify({"message": "Invalid date format"}), 400
    finally:
        session.close()

@maintenance_blueprint.route('/<int:maintenanceID>', methods=['DELETE'])
def delete_maintenance(maintenanceID):
    session = Session()
    try:
        m = session.query(Maintenance).filter_by(maintenanceID=maintenanceID).first()
        if not m:
            return jsonify({"message": "Maintenance not found"}), 404
        session.delete(m)
        session.commit()
        return jsonify({"message": "Maintenance deleted"}), 200
    except IntegrityError:
        session.rollback()
        return jsonify({"message": "Error deleting maintenance"}), 400
    finally:
        session.close()