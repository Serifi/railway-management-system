# employee_routes.py
from flask import Blueprint, jsonify, request
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload
from . import SessionLocal
from models.employee import Employee, Department, Role
from auth import login_user, logout_user, authenticate, authorize

employee_blueprint = Blueprint('employee_routes', __name__)

def serialize_employee(emp):
    """Serialize an Employee object into a dictionary."""
    return {
        "ssn": emp.ssn,
        "firstName": emp.firstName,
        "lastName": emp.lastName,
        "department": emp.department.value if emp.department else None,
        "role": emp.role.value if emp.role else None,
        "username": emp.username
    }

@employee_blueprint.route('/login', methods=['POST'])
def login_employee():
    """Authenticate an employee and return a token."""
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
    """Logout an employee."""
    auth_header = request.headers.get('Authorization')
    token = auth_header.split(" ")[1] if " " in auth_header else auth_header
    logout_user(token)
    return jsonify({"message": "Logged out successfully"}), 200

@employee_blueprint.route('/', methods=['GET'])
@authenticate
@authorize(roles=['Employee', 'Admin'])
def get_employees():
    """Retrieve all employees."""
    with SessionLocal() as session:
        emps = session.query(Employee).all()
        serialized = [serialize_employee(emp) for emp in emps]
        return jsonify(serialized), 200

@employee_blueprint.route('/<string:username>', methods=['GET'])
@authenticate
@authorize(roles=['Employee', 'Admin'])
def get_employee_by_username(username):
    """Retrieve an employee by username."""
    with SessionLocal() as session:
        emp = session.query(Employee).filter_by(username=username).first()
        if not emp:
            return jsonify({"message": f"Employee '{username}' not found"}), 404
        return jsonify(serialize_employee(emp)), 200

@employee_blueprint.route('/', methods=['POST'])
@authenticate
@authorize(roles=['Admin'])
def create_employee():
    """Create a new employee."""
    data = request.get_json()
    required_fields = {'ssn', 'firstName', 'lastName', 'password', 'department', 'role'}

    if not data or not required_fields.issubset(data):
        missing = required_fields - data.keys()
        return jsonify({"message": f"Missing required fields: {', '.join(missing)}"}), 400

    with SessionLocal() as session:
        try:
            # Validate and assign department and role
            department = Department[data['department']]
            role = Role[data['role']]

            # Create Employee instance
            emp = Employee(
                ssn=data['ssn'],
                firstName=data['firstName'],
                lastName=data['lastName'],
                password=data['password'],
                department=department,
                role=role,
                username=data.get('username')  # Auto-generated if None
            )
            session.add(emp)
            session.commit()
            return jsonify({"message": "Employee created successfully"}), 201
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
    """Update an existing employee."""
    data = request.get_json()
    if not data:
        return jsonify({"message": "No data provided for update"}), 400

    with SessionLocal() as session:
        try:
            emp = session.query(Employee).filter_by(ssn=ssn).first()
            if not emp:
                return jsonify({"message": f"Employee with SSN '{ssn}' not found"}), 404

            # Update general fields
            for field in ['firstName', 'lastName', 'password', 'username']:
                if field in data:
                    setattr(emp, field, data[field])

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
            return jsonify({"message": "Employee updated successfully"}), 200
        except IntegrityError:
            session.rollback()
            return jsonify({"message": "Username must be unique"}), 400
        except ValueError as ve:
            session.rollback()
            return jsonify({"message": str(ve)}), 400

@employee_blueprint.route('/<string:ssn>', methods=['DELETE'])
@authenticate
@authorize(roles=['Admin'])
def delete_employee(ssn):
    """Delete an employee."""
    with SessionLocal() as session:
        emp = session.query(Employee).options(joinedload(Employee.maintenances)).filter_by(ssn=ssn).first()
        if not emp:
            return jsonify({"message": f"Employee with SSN '{ssn}' not found"}), 404

        # Check for existing maintenances
        if emp.maintenances:
            return jsonify({"message": "Cannot delete employee with existing maintenances"}), 400

        try:
            session.delete(emp)
            session.commit()
            return jsonify({"message": "Employee deleted successfully"}), 200
        except IntegrityError:
            session.rollback()
            return jsonify({"message": "Integrity error occurred while deleting the employee"}), 400