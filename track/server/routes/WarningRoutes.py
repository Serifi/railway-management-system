from flask import Blueprint, jsonify, request
from models.Warning import Warning
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

DATABASE_URL = f"sqlite:///{os.path.abspath('server/db/track.db')}"
engine = create_engine(DATABASE_URL, echo=True)
Session = sessionmaker(bind=engine)

warning_blueprint = Blueprint('warning_routes', __name__)

@warning_blueprint.route('/', methods=['GET'])
def get_warnings():
    session = Session()
    warnings = session.query(Warning).all()

    warning_list = [
        {
            'warningID': warning.warningID,
            'warningName': warning.warningName,
            'description': warning.description,
            'startDate': warning.startDate.strftime('%Y-%m-%d') if warning.startDate else None,
            'endDate': warning.endDate.strftime('%Y-%m-%d') if warning.endDate else None,
        }
        for warning in warnings
    ]

    return jsonify(warning_list)

@warning_blueprint.route('/<int:warning_id>', methods=['GET'])
def get_warning_by_id(warning_id):
    session = Session()
    warning = session.query(Warning).filter(Warning.warningID == warning_id).first()

    if not warning:
        return jsonify({"message": f"Warning mit ID {warning_id} nicht gefunden"}), 404

    return jsonify({
        'warningID': warning.warningID,
        'warningName': warning.warningName,
        'description': warning.description,
        'startDate': warning.startDate.strftime('%Y-%m-%d') if warning.startDate else None,
        'endDate': warning.endDate.strftime('%Y-%m-%d') if warning.endDate else None,
    })

@warning_blueprint.route('/', methods=['POST'])
def create_warning():
    data = request.get_json()

    if not data or not all(key in data for key in ['warningName', 'description', 'startDate', 'endDate']):
        return jsonify({"message": "Fehlende Daten: 'warningName', 'description', 'startDate' und 'endDate' werden benötigt"}), 400

    try:
        start_date = datetime.strptime(data['startDate'], '%Y-%m-%d').date()
        end_date = datetime.strptime(data['endDate'], '%Y-%m-%d').date()
    except ValueError:
        return jsonify({"message": "Ungültiges Datumformat. Bitte 'YYYY-MM-DD' verwenden"}), 400

    if start_date >= end_date:
        return jsonify({"message": "Das Enddatum muss nach dem Startdatum liegen"}), 400

    new_warning = Warning(
        warningName=data['warningName'],
        description=data['description'],
        startDate=start_date,
        endDate=end_date
    )

    session = Session()
    session.add(new_warning)
    session.commit()

    return jsonify({
        'warningID': new_warning.warningID,
        'warningName': new_warning.warningName,
        'description': new_warning.description,
        'startDate': new_warning.startDate.strftime('%Y-%m-%d'),
        'endDate': new_warning.endDate.strftime('%Y-%m-%d')
    }), 201

"""
@warning_blueprint.route('/<int:warning_id>', methods=['PUT'])
def update_warning(warning_id):
    data = request.get_json()

    session = Session()
    warning = session.query(Warning).filter(Warning.warningID == warning_id).first()

    if not warning:
        return jsonify({"message": f"Warning mit ID {warning_id} nicht gefunden"}), 404

    if 'warningName' in data:
        warning.warningName = data['warningName']
    if 'description' in data:
        warning.description = data['description']
    if 'startDate' in data:
        warning.startDate = datetime.strptime(data['startDate'], '%Y-%m-%d').date()
    if 'endDate' in data:
        warning.endDate = datetime.strptime(data['endDate'], '%Y-%m-%d').date()

    session.commit()

    return jsonify({
        'warningID': warning.warningID,
        'warningName': warning.warningName,
        'description': warning.description,
        'startDate': warning.startDate.strftime('%Y-%m-%d'),
        'endDate': warning.endDate.strftime('%Y-%m-%d')
    }), 200
"""

@warning_blueprint.route('/<int:warning_id>', methods=['DELETE'])
def delete_warning(warning_id):
    session = Session()
    warning = session.query(Warning).filter(Warning.warningID == warning_id).first()

    if not warning:
        return jsonify({"message": f"Warnung mit ID {warning_id} nicht gefunden"}), 404

    session.delete(warning)
    session.commit()

    return jsonify({"message": f"Warnung mit ID {warning_id} wurde erfolgreich gelöscht"}), 200