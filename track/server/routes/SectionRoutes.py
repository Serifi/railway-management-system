from flask import Blueprint, jsonify, request
from models.Section import Section
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.TrainStation import TrainStation
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
            'endStationID': section.startStationID
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
        'endStationID': section.startStationID
    })

@section_blueprint.route('/', methods=['POST'])
def create_section():
    session = Session()
    data = request.get_json()

    if not data or not all(key in data for key in ['usageFee', 'length', 'maxSpeed', 'trackGauge', 'startStationID', 'startStationID']):
        return jsonify({"message": "Fehlende Daten: 'usageFee', 'length', 'maxSpeed', 'trackGauge', 'startStationID', 'startStationID' werden benötigt"}), 400

    if data['trackGauge'] not in ['1000', '1435']:
        return jsonify({"message": "Ungültiger Wert für 'trackGauge'. Erlaubte Werte: '1000' oder '1435'"}), 400

    if data['startStationID'] == data['endStationID']:
        return jsonify({"message": "Der Startbahnhof und Endbahnhof dürfen nicht identisch sein"}), 400

    start_station = session.query(TrainStation).filter(TrainStation.stationID == data['startStationID']).first()
    end_station = session.query(TrainStation).filter(TrainStation.stationID == data['endStationID']).first()

    if not start_station:
        return jsonify({"message": f"Startbahnhof mit ID {data['startStationID']} existiert nicht"}), 400
    if not end_station:
        return jsonify({"message": f"Endbahnhof mit ID {data['endStationID']} existiert nicht"}), 400

    new_section = Section(
        usageFee=data['usageFee'],
        length=data['length'],
        maxSpeed=data['maxSpeed'],
        trackGauge=data['trackGauge'],
        startStationID=data['startStationID'],
        endStationID=data['endStationID']
    )

    session = Session()
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

@section_blueprint.route('/<int:section_id>', methods=['PUT'])
def update_section(section_id):
    data = request.get_json()

    if not data or not all(key in data for key in ['usageFee', 'length', 'maxSpeed', 'trackGauge', 'startStationID', 'endStationID']):
        return jsonify({"message": "Fehlende Daten: 'usageFee', 'length', 'maxSpeed', 'trackGauge', 'startStationID', 'endStationID' werden benötigt"}), 400

    if data['trackGauge'] not in ['1000', '1435']:
        return jsonify({"message": "Ungültiger Wert für 'trackGauge'. Erlaubte Werte: '1000' oder '1435'"}), 400

    if data['startStationID'] == data['endStationID']:
        return jsonify({"message": "Der Startbahnhof und Endbahnhof dürfen nicht identisch sein"}), 400

    session = Session()
    section = session.query(Section).filter(Section.sectionID == section_id).first()

    start_station = session.query(TrainStation).filter(TrainStation.stationID == data['startStationID']).first()
    end_station = session.query(TrainStation).filter(TrainStation.stationID == data['endStationID']).first()

    if not start_station:
        return jsonify({"message": f"Startbahnhof mit ID {data['startStationID']} existiert nicht"}), 400
    if not end_station:
        return jsonify({"message": f"Endbahnhof mit ID {data['endStationID']} existiert nicht"}), 400

    if not section:
        return jsonify({"message": f"Section mit ID {section_id} nicht gefunden"}), 404

    if 'usageFee' in data:
        section.usageFee = data['usageFee']
    if 'length' in data:
        section.length = data['length']
    if 'maxSpeed' in data:
        section.maxSpeed = data['maxSpeed']
    if 'trackGauge' in data:
        section.trackGauge = data['trackGauge']
    if 'startStationID' in data:
        section.startStationID = data['startStationID']
    if 'endStationID' in data:
        section.endStationID = data['endStationID']

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

@section_blueprint.route('/<int:section_id>', methods=['DELETE'])
def delete_section(section_id):
    session = Session()
    section = session.query(Section).filter(Section.sectionID == section_id).first()

    if not section:
        return jsonify({"message": f"Section mit ID {section_id} nicht gefunden"}), 404

    session.delete(section)
    session.commit()

    return jsonify({"message": f"Section mit ID {section_id} wurde erfolgreich gelöscht"}), 200