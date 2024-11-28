from sqlite3 import IntegrityError

from flask import Blueprint, jsonify, request
from models.Department import Department
from models.Role import Role
import re

employee_blueprint = Blueprint('employee_routes', __name__)

from flask import Blueprint, jsonify, request
from models.Employee import Employee, Session

employee_blueprint = Blueprint('employee_routes', __name__)

# Login-Endpoint
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

    if employee.password != password:
        return jsonify({"message": "Benutzername oder Passwort falsch"}), 401

    return jsonify({"message": "Erfolgreich eingeloggt"}), 200

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

@employee_blueprint.route('/<int:ssn>', methods=['GET'])
def get_employee_by_ssn(ssn):
    session = Session()
    employee = session.query(Employee).filter(Employee.ssn == ssn).first()

    if not employee:
        return jsonify({"message": f"Mitarbeiter mit SSN {ssn} nicht gefunden"}), 404

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

    if not data or not data.get('ssn') or not data.get('firstName') or not data.get('lastName') or not data.get('password') or not data.get('department') or not data.get('role'):
        return jsonify({"message": "Fehlende Daten: 'ssn', 'firstName', 'lastName', 'password', 'department' und 'role' werden benötigt"}), 400

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

    existing_ssn = session.query(Employee).filter(Employee.ssn == data['ssn']).first()
    if existing_ssn:
        return jsonify({"message": "SSN ist nicht eindeutig"}), 400

    ssn_pattern = r"^\d{4}(0[1-9]|[12][0-9]|3[01])(0[1-9]|1[0-2])\d{2}$"
    if not re.match(ssn_pattern, str(data['ssn'])):
        return jsonify({"message": "SSN entspricht nicht den oesterreichischen Richtlinien"}), 400

    if 'username' in data and data['username']:
        username = data['username']
    else:
        username = f"{data['firstName'].lower()}.{data['lastName'].lower()}"

    existing_user = session.query(Employee).filter(Employee.username == username).first()
    if existing_user:
        return jsonify({"message": f"Username '{username}' ist nicht eindeutig"}), 400

    new_employee = Employee(
        ssn=data['ssn'],
        firstName=data['firstName'],
        lastName=data['lastName'],
        password=data['password'],
        department=department_enum,
        role=role_enum,
        username=username
    )

    try:
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
    except IntegrityError:
        session.rollback()
        return jsonify({"message": "Fehler beim Erstellen des Mitarbeiters."}), 500

@employee_blueprint.route('/<int:ssn>', methods=['PUT'])
def update_employee(ssn):
    data = request.get_json()

    session = Session()
    employee = session.query(Employee).filter(Employee.ssn == ssn).first()

    if not employee:
        return jsonify({"message": f"Mitarbeiter mit SSN {ssn} nicht gefunden"}), 404

    if 'firstName' in data or 'lastName' in data or 'username' in data:
        new_first_name = data.get('firstName', employee.firstName)
        new_last_name = data.get('lastName', employee.lastName)

        if 'username' in data and data['username']:
            new_username = data['username']
        else:
            new_username = f"{new_first_name.lower()}.{new_last_name.lower()}"

        existing_user = session.query(Employee).filter(
            Employee.username == new_username,
            Employee.ssn != ssn
        ).first()
        if existing_user:
            return jsonify({"message": f"Benutzername '{new_username}' existiert bereits."}), 400

        employee.firstName = new_first_name
        employee.lastName = new_last_name
        employee.username = new_username

    if 'password' in data:
        employee.password = data['password']

    if 'department' in data:
        try:
            employee.department = Department[data['department']]
        except KeyError:
            return jsonify({
                "message": f"Ungültiger Wert für 'department'. Erlaubte Werte: {[e.value for e in Department]}"
            }), 400

    if 'role' in data:
        try:
            employee.role = Role[data['role']]
        except KeyError:
            return jsonify({
                "message": f"Ungültiger Wert für 'role'. Erlaubte Werte: {[e.value for e in Role]}"
            }), 400

    session.commit()

    return jsonify({
        'ssn': employee.ssn,
        'firstName': employee.firstName,
        'lastName': employee.lastName,
        'department': employee.department.value,
        'role': employee.role.value,
        'username': employee.username
    }), 200

@employee_blueprint.route('/<int:ssn>', methods=['DELETE'])
def delete_employee(ssn):
    session = Session()
    employee = session.query(Employee).filter(Employee.ssn == ssn).first()

    if not employee:
        return jsonify({"message": f"Mitarbeiter mit SSN {ssn} nicht gefunden"}), 404

    session.delete(employee)
    session.commit()

    return jsonify({"message": f"Mitarbeiter mit SSN {ssn} wurde erfolgreich gelöscht"}), 200
