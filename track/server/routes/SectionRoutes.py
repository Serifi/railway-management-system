from flask import Blueprint, jsonify, request
from models.Section import Section, validate_station
from models.Warning import Warning
from models.SectionWarning import section_warning
from models.TrackSection import track_section
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import exists, select
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
        warnings_query = session.query(Warning).join(section_warning).filter(section_warning.c.sectionID == section.sectionID).all()

        warnings_list = [
            {
                "warningID": warning.warningID,
                "warningName": warning.warningName,
                "description": warning.description,
                "startDate": warning.startDate,
                "endDate": warning.endDate
            }
            for warning in warnings_query
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

    warnings_query = session.query(Warning).join(section_warning).filter(section_warning.c.sectionID == section_id).all()

    warnings_list = [
        {
            "warningID": warning.warningID,
            "warningName": warning.warningName,
            "description": warning.description,
            "startDate": warning.startDate,
            "endDate": warning.endDate
        }
        for warning in warnings_query
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

    try:
        start_station_id = validate_station(session, 'startStationID', data['startStationID'])
        end_station_id = validate_station(session, 'endStationID', data['endStationID'], start_station_id=start_station_id)

        new_section = Section(
            usageFee=data['usageFee'],
            length=data['length'],
            maxSpeed=data['maxSpeed'],
            trackGauge=data['trackGauge'],
            startStationID=start_station_id,
            endStationID=end_station_id
        )
        session.add(new_section)

        if 'warningIDs' in data:
            for warning_id in data['warningIDs']:
                warning = session.query(Warning).filter(Warning.warningID == warning_id).first()
                if not warning:
                    session.rollback()
                    return jsonify({"message": f"Warning mit ID {warning_id} existiert nicht"}), 400

                session.execute(section_warning.insert().values(sectionID=new_section.sectionID, warningID=warning_id))

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

    except ValueError as e:
        session.rollback()
        return jsonify({"message": str(e)}), 400
    finally:
        session.close()

@section_blueprint.route('/<int:section_id>', methods=['PUT'])
def update_section(section_id):
    session = Session()
    section = session.query(Section).filter(Section.sectionID == section_id).first()

    if not section:
        return jsonify({"message": f"Section mit ID {section_id} nicht gefunden"}), 404

    section_in_use = session.query(exists().where(track_section.c.sectionID == section_id)).scalar()
    if section_in_use:
        return jsonify({"message": "Abschnitt ist aktuell in Verwendung und kann nicht bearbeitet werden"}), 400

    data = request.get_json()
    try:
        if 'startStationID' in data:
            section.startStationID = validate_station(session, 'startStationID', data['startStationID'])
        if 'endStationID' in data:
            section.endStationID = validate_station(session, 'endStationID', data['endStationID'], start_station_id=section.startStationID)
        if 'usageFee' in data:
            section.usageFee = data['usageFee']
        if 'length' in data:
            section.length = data['length']
        if 'maxSpeed' in data:
            section.maxSpeed = data['maxSpeed']
        if 'trackGauge' in data:
            section.trackGauge = data['trackGauge']

        if 'warningIDs' in data:
            session.execute(section_warning.delete().where(section_warning.c.sectionID == section_id))
            for warning_id in data['warningIDs']:
                warning = session.query(Warning).filter(Warning.warningID == warning_id).first()
                if not warning:
                    session.rollback()
                    return jsonify({"message": f"Warning mit ID {warning_id} existiert nicht"}), 400
                session.execute(section_warning.insert().values(sectionID=section.sectionID, warningID=warning_id))

        session.commit()
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
        session.rollback()
        return jsonify({"message": str(e)}), 400
    finally:
        session.close()

@section_blueprint.route('/<int:section_id>', methods=['DELETE'])
def delete_section(section_id):
    session = Session()
    section = session.query(Section).filter(Section.sectionID == section_id).first()

    if not section:
        return jsonify({"message": f"Section mit ID {section_id} nicht gefunden"}), 404

    section_in_use = session.query(exists().where(track_section.c.sectionID == section_id)).scalar()
    if section_in_use:
        return jsonify({"message": "Abschnitt ist aktuell in Verwendung und kann nicht gelöscht werden"}), 400

    try:
        session.execute(section_warning.delete().where(section_warning.c.sectionID == section_id))
        session.delete(section)
        session.commit()
        return jsonify({"message": f"Section mit ID {section_id} wurde erfolgreich gelöscht"}), 200
    except Exception as e:
        session.rollback()
        return jsonify({"message": f"Fehler beim Löschen des Abschnitts: {str(e)}"}), 500
    finally:
        session.close()