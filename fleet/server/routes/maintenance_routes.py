# maintenance_routes.py

from flask import Blueprint, request, jsonify
from sqlalchemy.exc import IntegrityError
from . import SessionLocal
from models.maintenance import Maintenance
from models.employee import Employee, Department
from models.train import Train
from datetime import datetime
from auth import authenticate, authorize

maintenance_blueprint = Blueprint('maintenance_routes', __name__)

def serialize_maintenance(maintenance):
    """Serialize a Maintenance object into a dictionary."""
    return {
        "maintenanceID": maintenance.maintenanceID,
        "employeeSSN": maintenance.employeeSSN,
        "trainID": maintenance.trainID,
        "from_time": maintenance.from_time.isoformat(),
        "to_time": maintenance.to_time.isoformat()
    }

def parse_iso_datetime(date_str):
    """Parse an ISO formatted datetime string."""
    try:
        return datetime.fromisoformat(date_str)
    except ValueError:
        return None

@maintenance_blueprint.route('/', methods=['GET'])
@authenticate
@authorize(roles=['Employee', 'Admin'])
def get_maintenances():
    """Retrieve all maintenance records."""
    with SessionLocal() as session:
        maintenances = session.query(Maintenance).all()
        serialized = [serialize_maintenance(m) for m in maintenances]
        return jsonify(serialized), 200

@maintenance_blueprint.route('/<int:maintenance_id>', methods=['GET'])
@authenticate
@authorize(roles=['Employee', 'Admin'])
def get_maintenance_by_id(maintenance_id):
    """Retrieve a maintenance record by ID."""
    with SessionLocal() as session:
        maintenance = session.query(Maintenance).filter_by(maintenanceID=maintenance_id).first()
        if not maintenance:
            return jsonify({"message": f"Maintenance with ID {maintenance_id} not found"}), 404

        return jsonify(serialize_maintenance(maintenance)), 200

@maintenance_blueprint.route('/', methods=['POST'])
@authenticate
@authorize(roles=['Admin'])
def create_maintenance():
    """Create a new maintenance record with validations."""
    data = request.get_json()
    required_fields = {'employeeSSN', 'trainID', 'from_time', 'to_time'}

    if not data or not required_fields.issubset(data):
        missing = required_fields - data.keys()
        return jsonify({"message": f"Missing required fields: {', '.join(missing)}"}), 400

    employee_ssn = data['employeeSSN']
    train_id = data['trainID']
    from_time_str = data['from_time']
    to_time_str = data['to_time']

    from_time = parse_iso_datetime(from_time_str)
    to_time = parse_iso_datetime(to_time_str)

    if not from_time or not to_time:
        return jsonify({"message": "Invalid date format. Use ISO format (YYYY-MM-DDTHH:MM:SS)"}), 400

    if from_time >= to_time:
        return jsonify({"message": "from_time must be strictly before to_time"}), 400

    with SessionLocal() as session:
        try:
            # Validate Employee existence and department
            employee = session.query(Employee).filter_by(ssn=employee_ssn).first()
            if not employee:
                return jsonify({"message": "Employee not found"}), 404

            if employee.department != Department.Maintenance:
                return jsonify({"message": "Only Maintenance department employees can perform maintenances"}), 400

            # Validate Train existence
            train = session.query(Train).filter_by(trainID=train_id).first()
            if not train:
                return jsonify({"message": "Train not found"}), 404

            # Check for overlapping maintenances for this employee
            overlap = session.query(Maintenance).filter(
                Maintenance.employeeSSN == employee_ssn,
                Maintenance.from_time < to_time,
                Maintenance.to_time > from_time
            ).first()

            if overlap:
                return jsonify({"message": "Employee already assigned to overlapping maintenance time"}), 400

            # Create Maintenance
            maintenance = Maintenance(
                employeeSSN=employee_ssn,
                trainID=train_id,
                from_time=from_time,
                to_time=to_time
            )
            session.add(maintenance)
            session.commit()

            return jsonify({"message": "Maintenance created successfully"}), 201

        except IntegrityError:
            session.rollback()
            return jsonify({"message": "Integrity error occurred while creating maintenance"}), 400

@maintenance_blueprint.route('/<int:maintenance_id>', methods=['PUT'])
@authenticate
@authorize(roles=['Admin'])
def update_maintenance(maintenance_id):
    """Update an existing maintenance record with validations."""
    data = request.get_json()
    if not data:
        return jsonify({"message": "No data provided for update"}), 400

    with SessionLocal() as session:
        try:
            maintenance = session.query(Maintenance).filter_by(maintenanceID=maintenance_id).first()
            if not maintenance:
                return jsonify({"message": f"Maintenance with ID {maintenance_id} not found"}), 404

            # Update employeeSSN if provided
            if 'employeeSSN' in data:
                new_ssn = data['employeeSSN']
                employee = session.query(Employee).filter_by(ssn=new_ssn).first()
                if not employee:
                    return jsonify({"message": "Employee not found"}), 404
                if employee.department != Department.Maintenance:
                    return jsonify({"message": "Only Maintenance department employees can perform maintenances"}), 400
                maintenance.employeeSSN = new_ssn

            # Update trainID if provided
            if 'trainID' in data:
                new_train_id = data['trainID']
                train = session.query(Train).filter_by(trainID=new_train_id).first()
                if not train:
                    return jsonify({"message": "Train not found"}), 404
                maintenance.trainID = new_train_id

            # Update from_time and to_time if provided
            from_time = maintenance.from_time
            to_time = maintenance.to_time

            if 'from_time' in data:
                parsed_from_time = parse_iso_datetime(data['from_time'])
                if not parsed_from_time:
                    return jsonify({"message": "Invalid date format for from_time"}), 400
                from_time = parsed_from_time
                maintenance.from_time = from_time

            if 'to_time' in data:
                parsed_to_time = parse_iso_datetime(data['to_time'])
                if not parsed_to_time:
                    return jsonify({"message": "Invalid date format for to_time"}), 400
                to_time = parsed_to_time
                maintenance.to_time = to_time

            if from_time >= to_time:
                return jsonify({"message": "from_time must be strictly before to_time"}), 400

            # Check for overlapping maintenances for this employee excluding current maintenance
            overlap = session.query(Maintenance).filter(
                Maintenance.maintenanceID != maintenance_id,
                Maintenance.employeeSSN == maintenance.employeeSSN,
                Maintenance.from_time < to_time,
                Maintenance.to_time > from_time
            ).first()

            if overlap:
                return jsonify({"message": "Employee already assigned to overlapping maintenance time"}), 400

            session.commit()
            return jsonify({"message": "Maintenance updated successfully"}), 200

        except IntegrityError:
            session.rollback()
            return jsonify({"message": "Integrity error occurred while updating maintenance"}), 400

@maintenance_blueprint.route('/<int:maintenance_id>', methods=['DELETE'])
@authenticate
@authorize(roles=['Admin'])
def delete_maintenance(maintenance_id):
    """Delete a maintenance record."""
    with SessionLocal() as session:
        maintenance = session.query(Maintenance).filter_by(maintenanceID=maintenance_id).first()
        if not maintenance:
            return jsonify({"message": f"Maintenance with ID {maintenance_id} not found"}), 404

        try:
            session.delete(maintenance)
            session.commit()
            return jsonify({"message": "Maintenance deleted successfully"}), 200
        except IntegrityError:
            session.rollback()
            return jsonify({"message": "Integrity error occurred while deleting maintenance"}), 400