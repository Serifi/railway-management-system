# Warning-Endpunkte
from flask import Blueprint, jsonify, request
from models.Warning import Warning
from models.SectionWarning import section_warning
from sqlalchemy import create_engine, delete
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timezone
import os

# Datenbankverbindung einrichten
DATABASE_URL = f"sqlite:///{os.path.abspath('server/db/track.db')}"
engine = create_engine(DATABASE_URL, echo=True)
Session = sessionmaker(bind=engine)

warning_blueprint = Blueprint('warning_routes', __name__)

# Endpoint: Alle Warnungen abrufen
@warning_blueprint.route('/', methods=['GET'])
def get_warnings():
    session = Session()
    current_time = datetime.now(timezone.utc)

    # Entfernen abgelaufener Warnungen
    expired_warnings = session.query(Warning.warningID).filter(Warning.endDate < current_time, Warning.endDate.isnot(None)).all()
    expired_ids = [warning.warningID for warning in expired_warnings]

    if expired_ids:
        # Verknüpfungen in der Zwischentabelle löschen
        session.execute(delete(section_warning).where(section_warning.c.warningID.in_(expired_ids)))
        # Abgelaufene Warnungen löschen
        session.query(Warning).filter(Warning.warningID.in_(expired_ids)).delete(synchronize_session='fetch')
        session.commit()

    # Abrufen aktiver Warnungen
    warnings = session.query(Warning).filter((Warning.endDate >= current_time) | (Warning.endDate.is_(None))).all()

    # Liste der Warnungen erstellen
    warning_list = [
        {
            'warningID': warning.warningID,
            'warningName': warning.warningName,
            'description': warning.description,
            'startDate': warning.startDate.strftime('%Y-%m-%d %H:%M:%S'),
            'endDate': warning.endDate.strftime('%Y-%m-%d %H:%M:%S') if warning.endDate else None,
        }
        for warning in warnings
    ]

    return jsonify(warning_list)

# Endpoint: Warnung anhand der ID abrufen
@warning_blueprint.route('/<int:warning_id>', methods=['GET'])
def get_warning_by_id(warning_id):
    session = Session()
    current_time = datetime.now()

    # Abrufen einer einzelnen Warnung, wenn sie noch aktiv ist
    warning = session.query(Warning).filter(
        Warning.warningID == warning_id,
        Warning.endDate > current_time
    ).first()

    # Überprüfung, ob die Warnung existiert und aktiv ist
    if not warning:
        return jsonify({"message": f"Warnung mit ID {warning_id} nicht gefunden oder abgelaufen"}), 404

    return jsonify({
        'warningID': warning.warningID,
        'warningName': warning.warningName,
        'description': warning.description,
        'startDate': warning.startDate.strftime('%Y-%m-%d %H:%M:%S'),
        'endDate': warning.endDate.strftime('%Y-%m-%d %H:%M:%S') if warning.endDate else None,
    })

# Endpoint: Neue Warnung erstellen
@warning_blueprint.route('/', methods=['POST'])
def create_warning():
    session = Session()
    data = request.get_json()

    try:
        # Überprüfung, ob eine Warnung mit demselben Namen existiert
        existing_warning = session.query(Warning).filter_by(warningName=data['warningName']).first()
        if existing_warning:
            raise ValueError("Der Name der Warnung muss eindeutig sein.")

        # Konvertierung der Daten in UTC-Datetime-Objekte
        start_date = datetime.strptime(data['startDate'], '%Y-%m-%d %H:%M:%S').replace(tzinfo=timezone.utc)
        end_date = (
            datetime.strptime(data['endDate'], '%Y-%m-%d %H:%M:%S').replace(tzinfo=timezone.utc)
            if data.get('endDate')
            else None
        )

        # Neue Warnung erstellen
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
            'endDate': new_warning.endDate.strftime('%Y-%m-%d %H:%M:%S') if new_warning.endDate else None,
        }), 201
    except ValueError as e:
        session.rollback()
        return jsonify({"message": str(e)}), 400
    except IntegrityError:
        session.rollback()
        return jsonify({"message": "Ein unerwarteter Fehler ist aufgetreten."}), 500
    except Exception as e:
        session.rollback()
        return jsonify({"message": f"Ein unerwarteter Fehler ist aufgetreten: {str(e)}"}), 500
    finally:
        session.close()