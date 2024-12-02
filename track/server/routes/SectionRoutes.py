from flask import Blueprint, jsonify, request
from models.Section import Section
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = f"sqlite:///{os.path.abspath('server/db/track.db')}"
engine = create_engine(DATABASE_URL, echo=True)
Session = sessionmaker(bind=engine)

section_blueprint = Blueprint('section_routes', __name__)

@section_blueprint.route('/', methods=['GET'])
def get_sections():
    session = Session()
    sections = session.query(Section).all()

    section_list = [
        {
            'sectionID': section.sectionID,
            'usageFee': section.usageFee,
            'length': section.length,
            'maxSpeed': section.maxSpeed,
            'trackGauge': section.trackGauge,
            'startStationID': section.startStationID,
            'endStationID': section.endStationID
        }
        for section in sections
    ]

    return jsonify(section_list)

@section_blueprint.route('/<int:section_id>', methods=['GET'])
def get_section_by_id(section_id):
    session = Session()
    section = session.query(Section).filter(Section.sectionID == section_id).first()

    if not section:
        return jsonify({"message": f"Section mit ID {section_id} nicht gefunden"}), 404

    return jsonify({
        'sectionID': section.sectionID,
        'usageFee': section.usageFee,
        'length': section.length,
        'maxSpeed': section.maxSpeed,
        'trackGauge': section.trackGauge,
        'startStationID': section.startStationID,
        'endStationID': section.endStationID
    })

@section_blueprint.route('/', methods=['POST'])
def create_section():
    session = Session()
    data = request.get_json()
    new_section = Section()

    try:
        new_section.usageFee = new_section.validate_usage_fee(data['usageFee'])
        new_section.length = new_section.validate_length(data['length'])
        new_section.maxSpeed = new_section.validate_max_speed(data['maxSpeed'])
        new_section.trackGauge = new_section.validate_track_gauge(data['trackGauge'])
        new_section.startStationID = new_section.validate_stations('startStationID', data['startStationID'], session)
        new_section.endStationID = new_section.validate_stations('endStationID', data['endStationID'], session)
    except ValueError as e:
        return jsonify({"message": str(e)}), 400

    session.add(new_section)
    session.commit()

    return jsonify({
        'sectionID': new_section.sectionID,
        'usageFee': new_section.usageFee,
        'length': new_section.length,
        'maxSpeed': new_section.maxSpeed,
        'trackGauge': new_section.trackGauge,
        'startStationID': new_section.startStationID,
        'endStationID': new_section.endStationID
    }), 201

"""
@section_blueprint.route('/<int:section_id>', methods=['PUT'])
def update_section(section_id):
    session = Session()
    section = session.query(Section).filter(Section.sectionID == section_id).first()

    if not section:
        return jsonify({"message": f"Section mit ID {section_id} nicht gefunden"}), 404

    data = request.get_json()

    # Vor dem Commit: Überprüfen, ob Start- und Endbahnhof nicht identisch sind
    if 'startStationID' in data and 'endStationID' in data:
        if data['startStationID'] == data['endStationID']:
            return jsonify({"message": "Start- und Endbahnhof dürfen nicht identisch sein"}), 400

    try:
        # Validierung und Aktualisierung der Werte
        if 'usageFee' in data:
            section.usageFee = section.validate_usage_fee(data['usageFee'])
        if 'length' in data:
            section.length = section.validate_length(data['length'])
        if 'maxSpeed' in data:
            section.maxSpeed = section.validate_max_speed(data['maxSpeed'])
        if 'trackGauge' in data:
            section.trackGauge = section.validate_track_gauge(data['trackGauge'])
        if 'startStationID' in data:
            section.startStationID = section.validate_stations('startStationID', data['startStationID'], session)
        if 'endStationID' in data:
            section.endStationID = section.validate_stations('endStationID', data['endStationID'], session)

        # Sicherstellen, dass es keinen Constraint-Verstoß gibt, bevor Änderungen commitet werden
        session.flush()  # Stellt sicher, dass alle Änderungen im Arbeitsspeicher sind, ohne sie in die DB zu schreiben

        session.commit()  # Jetzt Commit durchführen

        # Rückgabe der aktualisierten Sektion als JSON
        return jsonify({
            'sectionID': section.sectionID,
            'usageFee': section.usageFee,
            'length': section.length,
            'maxSpeed': section.maxSpeed,
            'trackGauge': section.trackGauge,
            'startStationID': section.startStationID,
            'endStationID': section.endStationID
        }), 200

    except ValueError as e:
        session.rollback()  # Rollback bei Fehler
        return jsonify({"message": str(e)}), 400
"""

@section_blueprint.route('/<int:section_id>', methods=['DELETE'])
def delete_section(section_id):
    session = Session()
    section = session.query(Section).filter(Section.sectionID == section_id).first()

    if not section:
        return jsonify({"message": f"Section mit ID {section_id} nicht gefunden"}), 404

    session.delete(section)
    session.commit()

    return jsonify({"message": f"Section mit ID {section_id} wurde erfolgreich gelöscht"}), 200