from flask import Blueprint, jsonify, request
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload

from . import SessionLocal
from models.employee import Employee, Department, Role
from auth import login_user, logout_user, authenticate, authorize

employee_blueprint = Blueprint('employee_routes', __name__)

def serialize_employee(emp, include_password=False):
    """ Serialize an Employee object into a dictionary """
    serialized = {
        "ssn": emp.ssn,
        "firstName": emp.firstName,
        "lastName": emp.lastName,
        "department": emp.department.value if emp.department else None,
        "role": emp.role.value if emp.role else None,
        "username": emp.username
    }
    if include_password:
        serialized["password"] = emp.password
    return serialized


@employee_blueprint.route('/login', methods=['POST'])
def login_employee():
    """ Login an employee by generating their token """
    data = request.get_json()
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({"message": "Username and password are required"}), 400

    with SessionLocal() as session:
        emp = session.query(Employee).filter_by(username=data['username']).first()
        if not emp or emp.password != data['password']:
            return jsonify({"message": "Incorrect username or password"}), 401

        token = login_user(emp)
        return jsonify({"message": "Logged in successfully", "token": token}), 200


@employee_blueprint.route('/logout', methods=['POST'])
@authenticate
@authorize(roles=['Employee', 'Admin'])
def logout_employee():
    """ Logout an employee by invalidating their token """
    auth_header = request.headers.get('Authorization')
    token = auth_header.split(" ")[1] if " " in auth_header else auth_header
    logout_user(token)
    return jsonify({"message": "Logged out successfully"}), 200


@employee_blueprint.route('/', methods=['GET'])
@authenticate
@authorize(roles=['Employee', 'Admin'])
def get_employees():
    """ Retrieve all employees """
    with SessionLocal() as session:
        emps = session.query(Employee).all()
        serialized = [serialize_employee(emp) for emp in emps]
        return jsonify(serialized), 200


@employee_blueprint.route('/<string:username>', methods=['GET'])
@authenticate
@authorize(roles=['Employee', 'Admin'])
def get_employee_by_username(username):
    """ Retrieve an employee by username with password """
    with SessionLocal() as session:
        emp = session.query(Employee).filter_by(username=username).first()
        if not emp:
            return jsonify({"message": f"Employee '{username}' not found"}), 404
        return jsonify(serialize_employee(emp, include_password=True)), 200


@employee_blueprint.route('/', methods=['POST'])
@authenticate
@authorize(roles=['Admin'])
def create_employee():
    """ Create a new employee """
    data = request.get_json()
    required_fields = {'ssn', 'firstName', 'lastName', 'password', 'department', 'role'}

    # Check missing fields
    if not data or not required_fields.issubset(data):
        missing = required_fields - data.keys()
        return jsonify({"message": f"Missing required fields: {', '.join(missing)}"}), 400

    with SessionLocal() as session:
        try:
            # Check if SSN is already taken
            if session.query(Employee).filter_by(ssn=data['ssn']).first():
                return jsonify({"message": "SSN is already taken"}), 400

            # Validate and assign department and role
            department = Department[data['department']]
            role = Role[data['role']]

            # Generate a unique username
            base_username = data.get('username') or f"{data['firstName']}.{data['lastName']}".lower()
            username = base_username
            counter = 1
            while session.query(Employee).filter_by(username=username).first():
                username = f"{base_username}{counter}" # Append counter if username exists: test.test1, test.test2, ...
                counter += 1

            # Create Employee
            emp = Employee(
                ssn=data['ssn'],
                firstName=data['firstName'],
                lastName=data['lastName'],
                password=data['password'],
                department=department,
                role=role,
                username=username
            )
            session.add(emp)
            session.commit()
            return jsonify({"message": f"Employee '{emp.username}' created successfully"}), 201

        except KeyError:
            session.rollback()
            return jsonify({"message": "Invalid department or role"}), 400
        except ValueError as ve:
            session.rollback()
            return jsonify({"message": str(ve)}), 400
        except IntegrityError:
            session.rollback()
            return jsonify({"message": "SSN or username must be unique"}), 400


@employee_blueprint.route('/<string:ssn>', methods=['PUT'])
@authenticate
@authorize(roles=['Admin'])
def update_employee(ssn):
    """ Update an existing employee """
    data = request.get_json()

    # Check if there is data to update
    if not data:
        return jsonify({"message": "No data provided for update"}), 400

    with SessionLocal() as session:
        try:
            # Fetch employee by SSN
            emp = session.query(Employee).filter_by(ssn=ssn).first()

            # Check if employee exists
            if not emp:
                return jsonify({"message": f"Employee with SSN '{ssn}' not found"}), 404

            # Update password if provided
            if 'password' in data:
                emp.password = data['password']

            # Update department if provided
            if 'department' in data:
                try:
                    emp.department = Department[data['department']]
                except KeyError:
                    return jsonify({"message": "Invalid department"}), 400

            # Update role if provided
            if 'role' in data:
                try:
                    emp.role = Role[data['role']]
                except KeyError:
                    return jsonify({"message": "Invalid role"}), 400

            session.commit()
            return jsonify({"message": "Employee updated successfully", "username": emp.username}), 200
        except IntegrityError as e:
            session.rollback()
            if 'username' in str(e.orig):
                return jsonify({"message": "Username already taken"}), 400
            return jsonify({"message": "Username must be unique"}), 400
        except ValueError as ve:
            session.rollback()
            return jsonify({"message": str(ve)}), 400


@employee_blueprint.route('/<string:ssn>', methods=['DELETE'])
@authenticate
@authorize(roles=['Admin'])
def delete_employee(ssn):
    """ Delete an employee """
    with SessionLocal() as session:
        emp = session.query(Employee).options(joinedload(Employee.maintenances)).filter_by(ssn=ssn).first()
        if not emp:
            return jsonify({"message": f"Employee with SSN '{ssn}' not found"}), 404

        # Check if employee has maintenances
        from datetime import datetime
        now = datetime.utcnow()
        active_maintenances = [
            m for m in emp.maintenances if hasattr(m, 'to_time') and m.to_time >= now
        ]

        if active_maintenances:
            return jsonify({"message": "Cannot delete employee with current or future maintenances"}), 400

        try:
            session.delete(emp)
            session.commit()
            return jsonify({"message": "Employee deleted successfully"}), 200
        except IntegrityError:
            session.rollback()
            return jsonify({"message": "Integrity error while deleting employee"}), 400