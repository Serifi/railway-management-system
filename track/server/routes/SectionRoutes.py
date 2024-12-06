from flask import Blueprint, jsonify, request
from models.Section import Section
from models.Warning import Warning
from models.SectionWarning import section_warning
from sqlalchemy import create_engine
from sqlalchemy.sql import text
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

    section_list = []
    for section in sections:
        warnings_query = text("""
            SELECT warning.warningID, warning.warningName, warning.description, 
                   warning.startDate, warning.endDate
            FROM section_warning
            JOIN warning ON section_warning.warningID = warning.warningID
            WHERE section_warning.sectionID = :sectionID
        """)
        warnings = session.execute(warnings_query, {"sectionID": section.sectionID}).fetchall()

        warnings_list = [
            {
                "warningID": warning.warningID,
                "warningName": warning.warningName,
                "description": warning.description,
                "startDate": warning.startDate,
                "endDate": warning.endDate
            }
            for warning in warnings
        ]

        section_list.append({
            'sectionID': section.sectionID,
            'usageFee': section.usageFee,
            'length': section.length,
            'maxSpeed': section.maxSpeed,
            'trackGauge': section.trackGauge,
            'startStationID': section.startStationID,
            'endStationID': section.endStationID,
            'warnings': warnings_list
        })
    return jsonify(section_list)

@section_blueprint.route('/<int:section_id>', methods=['GET'])
def get_section_by_id(section_id):
    session = Session()

    section = session.query(Section).filter(Section.sectionID == section_id).first()

    if not section:
        return jsonify({"message": f"Section mit ID {section_id} nicht gefunden"}), 404

    warnings_query = text("""
        SELECT warning.warningID, warning.warningName, warning.description, 
               warning.startDate, warning.endDate
        FROM section_warning
        JOIN warning ON section_warning.warningID = warning.warningID
        WHERE section_warning.sectionID = :sectionID
    """)
    warnings = session.execute(warnings_query, {"sectionID": section_id}).fetchall()

    warnings_list = [
        {
            "warningID": warning.warningID,
            "warningName": warning.warningName,
            "description": warning.description,
            "startDate": warning.startDate,
            "endDate": warning.endDate
        }
        for warning in warnings
    ]

    return jsonify({
        'sectionID': section.sectionID,
        'usageFee': section.usageFee,
        'length': section.length,
        'maxSpeed': section.maxSpeed,
        'trackGauge': section.trackGauge,
        'startStationID': section.startStationID,
        'endStationID': section.endStationID,
        'warnings': warnings_list
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

        session.add(new_section)
        session.commit()

        if 'warningIDs' in data:
            warning_ids = data['warningIDs']
            for warning_id in warning_ids:
                warning = session.query(Warning).filter(Warning.warningID == warning_id).first()

                if not warning:
                    session.rollback()
                    return jsonify({"message": f"Warning mit ID {warning_id} existiert nicht"}), 400

                session.execute(section_warning.insert().values(sectionID=new_section.sectionID, warningID=warning_id))

        session.commit()

    except ValueError as e:
        session.rollback()
        return jsonify({"message": str(e)}), 400

    return jsonify({
        'sectionID': new_section.sectionID,
        'usageFee': new_section.usageFee,
        'length': new_section.length,
        'maxSpeed': new_section.maxSpeed,
        'trackGauge': new_section.trackGauge,
        'startStationID': new_section.startStationID,
        'endStationID': new_section.endStationID
    }), 201

@section_blueprint.route('/<int:section_id>', methods=['PUT'])
def update_section(section_id):
    session = Session()
    section = session.query(Section).filter(Section.sectionID == section_id).first()

    if not section:
        return jsonify({"message": f"Section mit ID {section_id} nicht gefunden"}), 404

    data = request.get_json()

    if 'startStationID' in data and 'endStationID' in data:
        if data['startStationID'] == data['endStationID']:
            return jsonify({"message": "Der Startbahnhof und Endbahnhof dürfen nicht identisch sein"}), 400

    try:
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

        if 'warningIDs' in data:
            session.execute(section_warning.delete().where(section_warning.c.sectionID == section.sectionID))

            warning_ids = data['warningIDs']
            for warning_id in warning_ids:
                warning = session.query(Warning).filter(Warning.warningID == warning_id).first()

                if not warning:
                    session.rollback()
                    return jsonify({"message": f"Warning mit ID {warning_id} existiert nicht"}), 400

                session.execute(section_warning.insert().values(sectionID=section.sectionID, warningID=warning_id))

        session.commit()

    except ValueError as e:
        session.rollback()
        return jsonify({"message": str(e)}), 400

    return jsonify({
        'sectionID': section.sectionID,
        'usageFee': section.usageFee,
        'length': section.length,
        'maxSpeed': section.maxSpeed,
        'trackGauge': section.trackGauge,
        'startStationID': section.startStationID,
        'endStationID': section.endStationID
    }), 200

@section_blueprint.route('/<int:section_id>', methods=['DELETE'])
def delete_section(section_id):
    session = Session()
    section = session.query(Section).filter(Section.sectionID == section_id).first()

    if not section:
        return jsonify({"message": f"Section mit ID {section_id} nicht gefunden"}), 404

    session.delete(section)
    session.commit()

    return jsonify({"message": f"Section mit ID {section_id} wurde erfolgreich gelöscht"}), 200