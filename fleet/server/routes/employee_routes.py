import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from flask import Blueprint, jsonify, request
from models import Base
from models.employee import Base, Employee, Department, Role
import re

employee_blueprint = Blueprint('employee_routes', __name__)

DATABASE_URL = f"sqlite:///{os.path.abspath('server/db/fleet.db')}"
engine = create_engine(DATABASE_URL, echo=False)
Session = sessionmaker(bind=engine)
Base.metadata.create_all(engine)

@employee_blueprint.route('/login', methods=['POST'])
def login_employee():
    data = request.get_json()
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({"message": "Username and password required"}), 400

    session = Session()
    emp = session.query(Employee).filter_by(username=data['username']).first()
    if not emp or emp.password != data['password']:
        return jsonify({"message": "Wrong username or password"}), 401
    return jsonify({"message": "Logged in"}), 200

@employee_blueprint.route('/', methods=['GET'])
def get_employees():
    session = Session()
    emps = session.query(Employee).all()
    out = []
    for e in emps:
        out.append({
            "ssn": e.ssn,
            "firstName": e.firstName,
            "lastName": e.lastName,
            "department": e.department.value,
            "role": e.role.value,
            "username": e.username
        })
    return jsonify(out), 200

@employee_blueprint.route('/<string:username>', methods=['GET'])
def get_employee_by_username(username):
    session = Session()
    emp = session.query(Employee).filter_by(username=username).first()
    if not emp:
        return jsonify({"message": f"Employee {username} not found"}), 404
    return jsonify({
        "ssn": emp.ssn,
        "firstName": emp.firstName,
        "lastName": emp.lastName,
        "password": emp.password,
        "department": emp.department.value,
        "role": emp.role.value,
        "username": emp.username
    }), 200

@employee_blueprint.route('/', methods=['POST'])
def create_employee():
    data = request.get_json()
    for field in ['ssn','firstName','lastName','password','department','role']:
        if field not in data:
            return jsonify({"message": f"{field} required"}), 400

    # Validate department, role
    try:
        dept = Department[data['department']]
        rol = Role[data['role']]
    except KeyError:
        return jsonify({"message": "Invalid department or role"}), 400

    session = Session()
    if session.query(Employee).filter_by(ssn=data['ssn']).first():
        return jsonify({"message": "SSN not unique"}), 400

    ssn_pattern = r"^\d{4}(0[1-9]|[12][0-9]|3[01])(0[1-9]|1[0-2])\d{2}$"
    if not re.match(ssn_pattern, data['ssn']):
        return jsonify({"message": "SSN invalid"}), 400

    if data.get('username'):
        uname = data['username']
    else:
        uname = f"{data['firstName'].lower()}.{data['lastName'].lower()}"

    if session.query(Employee).filter_by(username=uname).first():
        return jsonify({"message": "Username not unique"}), 400

    e = Employee(
        ssn=data['ssn'],
        firstName=data['firstName'],
        lastName=data['lastName'],
        password=data['password'],
        department=dept,
        role=rol,
        username=uname
    )
    try:
        session.add(e)
        session.commit()
        return jsonify({"message": "Employee created"}), 201
    except IntegrityError:
        session.rollback()
        return jsonify({"message": "Error creating employee"}), 500

@employee_blueprint.route('/<int:ssn>', methods=['PUT'])
def update_employee(ssn):
    data = request.get_json()
    session = Session()
    e = session.query(Employee).filter_by(ssn=str(ssn)).first()
    if not e:
        return jsonify({"message": "Employee not found"}), 404

    if 'firstName' in data: e.firstName = data['firstName']
    if 'lastName' in data: e.lastName = data['lastName']
    if 'password' in data: e.password = data['password']

    if 'department' in data:
        try:
            e.department = Department[data['department']]
        except KeyError:
            return jsonify({"message": "Invalid department"}), 400

    if 'role' in data:
        try:
            e.role = Role[data['role']]
        except KeyError:
            return jsonify({"message": "Invalid role"}), 400

    if 'username' in data and data['username']:
        new_uname = data['username']
    else:
        new_uname = f"{e.firstName.lower()}.{e.lastName.lower()}"
    check = session.query(Employee).filter(Employee.username==new_uname, Employee.ssn!=str(ssn)).first()
    if check:
        return jsonify({"message": "Username not unique"}), 400
    e.username = new_uname

    session.commit()
    return jsonify({"message": "Employee updated"}), 200

@employee_blueprint.route('/<int:ssn>', methods=['DELETE'])
def delete_employee(ssn):
    session = Session()
    e = session.query(Employee).filter_by(ssn=str(ssn)).first()
    if not e:
        return jsonify({"message": "Employee not found"}), 404

    session.delete(e)
    session.commit()
    return jsonify({"message": "Employee deleted"}), 200