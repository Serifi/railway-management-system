from flask import Blueprint, jsonify, request
from models.Warning import Warning
from models.SectionWarning import section_warning
from sqlalchemy import create_engine, delete
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timezone
import os

DATABASE_URL = f"sqlite:///{os.path.abspath('server/db/track.db')}"
engine = create_engine(DATABASE_URL, echo=True)
Session = sessionmaker(bind=engine)

warning_blueprint = Blueprint('warning_routes', __name__)

@warning_blueprint.route('/', methods=['GET'])
def get_warnings():
    session = Session()
    current_time = datetime.now(timezone.utc)

    expired_warnings = session.query(Warning.warningID).filter(Warning.endDate < current_time).all()
    expired_ids = [warning.warningID for warning in expired_warnings]

    if expired_ids:
        session.execute(delete(section_warning).where(section_warning.c.warningID.in_(expired_ids)))
        session.query(Warning).filter(Warning.warningID.in_(expired_ids)).delete(synchronize_session='fetch')
        session.commit()

    warnings = session.query(Warning).filter(Warning.endDate >= current_time).all()

    warning_list = [
        {
            'warningID': warning.warningID,
            'warningName': warning.warningName,
            'description': warning.description,
            'startDate': warning.startDate.strftime('%Y-%m-%d %H:%M:%S'),
            'endDate': warning.endDate.strftime('%Y-%m-%d %H:%M:%S'),
        }
        for warning in warnings
    ]

    return jsonify(warning_list)

@warning_blueprint.route('/<int:warning_id>', methods=['GET'])
def get_warning_by_id(warning_id):
    session = Session()
    current_time = datetime.now()
    warning = session.query(Warning).filter(
        Warning.warningID == warning_id,
        Warning.endDate > current_time
    ).first()

    if not warning:
        return jsonify({"message": f"Warnung mit ID {warning_id} nicht gefunden oder abgelaufen"}), 404

    return jsonify({
        'warningID': warning.warningID,
        'warningName': warning.warningName,
        'description': warning.description,
        'startDate': warning.startDate.strftime('%Y-%m-%d %H:%M:%S'),
        'endDate': warning.endDate.strftime('%Y-%m-%d %H:%M:%S'),
    })

@warning_blueprint.route('/', methods=['POST'])
def create_warning():
    session = Session()
    data = request.get_json()

    if not data or not all(key in data for key in ['warningName', 'description', 'startDate', 'endDate']):
        return jsonify({"message": "Fehlende Daten: 'warningName', 'description', 'startDate' und 'endDate' werden benötigt"}), 400

    try:
        start_date = datetime.strptime(data['startDate'], '%Y-%m-%d %H:%M:%S')
        end_date = datetime.strptime(data['endDate'], '%Y-%m-%d %H:%M:%S')

        new_warning = Warning(
            warningName=data['warningName'],
            description=data['description'],
            startDate=start_date,
            endDate=end_date
        )

        session.add(new_warning)
        session.commit()

        return jsonify({
            'warningID': new_warning.warningID,
            'warningName': new_warning.warningName,
            'description': new_warning.description,
            'startDate': new_warning.startDate.strftime('%Y-%m-%d %H:%M:%S'),
            'endDate': new_warning.endDate.strftime('%Y-%m-%d %H:%M:%S'),
        }), 201

    except ValueError as e:
        session.rollback()
        return jsonify({"message": str(e)}), 400
    except Exception as e:
        session.rollback()
        return jsonify({"message": f"Ein unerwarteter Fehler ist aufgetreten: {str(e)}"}), 500
    finally:
        session.close()

@warning_blueprint.route('/<int:warning_id>', methods=['DELETE'])
def delete_warning(warning_id):
    session = Session()
    warning = session.query(Warning).filter(Warning.warningID == warning_id).first()

    if not warning:
        return jsonify({"message": f"Warnung mit ID {warning_id} nicht gefunden"}), 404

    session.delete(warning)
    session.commit()

    return jsonify({"message": f"Warnung mit ID {warning_id} wurde erfolgreich gelöscht"}), 200