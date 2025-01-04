from flask import Blueprint, jsonify, request
from models.Employee import Employee
from models.Department import Department
from models.Role import Role
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
import bcrypt
import os

DATABASE_URL = f"sqlite:///{os.path.abspath('server/db/track.db')}"
engine = create_engine(DATABASE_URL, echo=True)
Session = sessionmaker(bind=engine)
employee_blueprint = Blueprint('employee_routes', __name__)

@employee_blueprint.route('/login', methods=['POST'])
def login_employee():
    data = request.get_json()

    if not data or not data.get('username') or not data.get('password'):
        return jsonify({"message": "Benutzername und Passwort sind erforderlich"}), 400

    username = data['username']
    password = data['password']

    session = Session()
    employee = session.query(Employee).filter(Employee.username == username).first()

    if not employee:
        return jsonify({"message": "Benutzername oder Passwort falsch"}), 401

    if not bcrypt.checkpw(password.encode('utf-8'), employee.password.encode('utf-8')):
        return jsonify({"message": "Benutzername oder Passwort falsch"}), 401

    return jsonify({
        "message": "Erfolgreich eingeloggt",
        "username": employee.username,
        "role": employee.role.value,
        "department": employee.department.value,
        "firstName": employee.firstName,
        "lastName": employee.lastName,
    }), 200

@employee_blueprint.route('/', methods=['GET'])
def get_employees():
    session = Session()
    employees = session.query(Employee).all()

    employees_list = [
        {
            "ssn": emp.ssn,
            "firstName": emp.firstName,
            "lastName": emp.lastName,
            "department": emp.department.value,
            "role": emp.role.value,
            "username": emp.username
        }
        for emp in employees
    ]
    return jsonify(employees_list)

@employee_blueprint.route('/<string:username>', methods=['GET'])
def get_employee_by_username(username):
    session = Session()
    employee = session.query(Employee).filter(Employee.username == username).first()

    if not employee:
        return jsonify({"message": f"Mitarbeiter mit Benutzername {username} nicht gefunden"}), 404

    return jsonify({
        "ssn": employee.ssn,
        "firstName": employee.firstName,
        "lastName": employee.lastName,
        "password": employee.password,
        "department": employee.department.value,
        "role": employee.role.value,
        "username": employee.username
    })

@employee_blueprint.route('/', methods=['POST'])
def create_employee():
    data = request.get_json()
    if not data or not all(key in data for key in ['ssn', 'firstName', 'lastName', 'password', 'department', 'role']):
        return jsonify({"message": "Fehlende Daten: 'ssn', 'firstName', 'lastName', 'password', 'department' und 'role' werden benötigt"}), 400

    if len(data['password']) != 60:
        return jsonify({"message": "Das Passwort ist nicht korrekt gehasht"}), 400

    try:
        department_enum = Department[data['department']]
        role_enum = Role[data['role']]
    except KeyError:
        return jsonify({
            "message": f"Ungültige Werte für 'department' oder 'role'. Erlaubte Werte: "
                       f"'department': {[e.value for e in Department]}, "
                       f"'role': {[e.value for e in Role]}"
        }), 400

    session = Session()

    if 'username' in data and data['username']:
        username = data['username']
    else:
        username = f"{data['firstName'].lower()}.{data['lastName'].lower()}"

    existing_user = session.query(Employee).filter(Employee.username == username).first()
    if existing_user:
        session.rollback()
        return jsonify({"message": f"Benutzername '{username}' ist bereits vergeben"}), 400

    try:
        new_employee = Employee(
            ssn=data['ssn'],
            firstName=data['firstName'],
            lastName=data['lastName'],
            password=data['password'],
            department=department_enum,
            role=role_enum,
            username=username
        )
        session.add(new_employee)
        session.commit()
        return jsonify({
            'ssn': new_employee.ssn,
            'firstName': new_employee.firstName,
            'lastName': new_employee.lastName,
            'department': new_employee.department.value,
            'role': new_employee.role.value,
            'username': new_employee.username
        }), 201
    except ValueError as e:
        session.rollback()
        return jsonify({"message": str(e)}), 400
    except IntegrityError:
        session.rollback()
        return jsonify({"message": "Ein Fehler ist aufgetreten. Bitte versuchen Sie es erneut."}), 500

@employee_blueprint.route('/<int:ssn>', methods=['PUT'])
def update_employee(ssn):
    data = request.get_json()

    session = Session()
    employee = session.query(Employee).filter(Employee.ssn == ssn).first()

    if not employee:
        return jsonify({"message": f"Mitarbeiter mit SSN {ssn} nicht gefunden"}), 404

    try:
        if 'firstName' in data:
            employee.firstName = data['firstName']
        if 'lastName' in data:
            employee.lastName = data['lastName']
        if 'username' in data:
            new_username = data['username']
            existing_user = session.query(Employee).filter(
                Employee.username == new_username,
                Employee.ssn != ssn
            ).first()
            if existing_user:
                raise ValueError(f"Benutzername '{new_username}' existiert bereits.")
            employee.username = new_username
        if 'password' in data:
            if len(data['password']) != 60:
                raise ValueError("Das Passwort ist nicht valide")
            employee.password = data['password']
        if 'department' in data:
            employee.department = Department[data['department']]
        if 'role' in data:
            employee.role = Role[data['role']]

        session.commit()
        return jsonify({
            'ssn': employee.ssn,
            'firstName': employee.firstName,
            'lastName': employee.lastName,
            'department': employee.department.value,
            'role': employee.role.value,
            'username': employee.username
        }), 200
    except KeyError as e:
        session.rollback()
        return jsonify({
            "message": f"Ungültiger Wert für {str(e)}. Erlaubte Werte: {[e.value for e in Department] if 'department' in str(e) else [r.value for r in Role]}"
        }), 400
    except ValueError as e:
        session.rollback()
        return jsonify({"message": str(e)}), 400

@employee_blueprint.route('/<int:ssn>', methods=['DELETE'])
def delete_employee(ssn):
    session = Session()
    employee = session.query(Employee).filter(Employee.ssn == ssn).first()

    if not employee:
        return jsonify({"message": f"Mitarbeiter mit SSN {ssn} nicht gefunden"}), 404

    session.delete(employee)
    session.commit()

    return jsonify({"message": f"Mitarbeiter mit SSN {ssn} wurde erfolgreich gelöscht"}), 200