from flask import Blueprint, jsonify, request
from models.Employee import Employee, Session

employee_blueprint = Blueprint('employee_routes', __name__)

@employee_blueprint.route('/', methods=['GET'])
def get_employees():
    session = Session()
    employees = session.query(Employee).all()

    employees_list = [
        {
            "ssn": emp.ssn,
            "firstName": emp.firstName,
            "lastName": emp.lastName,
            "department": emp.department,
            "role": emp.role
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
        "department": employee.department,
        "role": employee.role
    })

@employee_blueprint.route('/', methods=['POST'])
def create_employee():
    data = request.get_json()

    if not data or not data.get('ssn') or not data.get('firstName') or not data.get('lastName') or not data.get('password') or not data.get('department') or not data.get('role'):
        return jsonify({"message": "Fehlende Daten: 'ssn', 'firstName', 'lastName', 'password', 'department' und 'role' werden benötigt"}), 400

    new_employee = Employee(
        ssn=data['ssn'],
        firstName=data['firstName'],
        lastName=data['lastName'],
        password=data['password'],
        department=data['department'],
        role=data['role']
    )

    session = Session()
    session.add(new_employee)
    session.commit()

    return jsonify({
        'ssn': new_employee.ssn,
        'firstName': new_employee.firstName,
        'lastName': new_employee.lastName,
        'department': new_employee.department,
        'role': new_employee.role
    }), 201

@employee_blueprint.route('/<int:ssn>', methods=['PUT'])
def update_employee(ssn):
    data = request.get_json()

    session = Session()
    employee = session.query(Employee).filter(Employee.ssn == ssn).first()

    if not employee:
        return jsonify({"message": f"Mitarbeiter mit SSN {ssn} nicht gefunden"}), 404


    if 'firstName' in data:
        employee.firstName = data['firstName']
    if 'lastName' in data:
        employee.lastName = data['lastName']
    if 'password' in data:
        employee.password = data['password']
    if 'department' in data:
        employee.department = data['department']
    if 'role' in data:
        employee.role = data['role']

    session.commit()

    return jsonify({
        'ssn': employee.ssn,
        'firstName': employee.firstName,
        'lastName': employee.lastName,
        'department': employee.department,
        'role': employee.role
    }), 200

@employee_blueprint.route('/<int:ssn>', methods=['DELETE'])
def delete_employee(ssn):
    session = Session()
    employee = session.query(Employee).filter(Employee.ssn == ssn).first()

    if not employee:
        return jsonify({"message": f"Mitarbeiter mit SSN {ssn} nicht gefunden"}), 404

    session.delete(employee)
    session.commit()

    return jsonify({"message": f"Mitarbeiter mit SSN {ssn} wurde erfolgreich gelöscht"}), 200  # Erfolgreich gelöscht, Statuscode 200
