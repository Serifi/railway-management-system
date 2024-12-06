from flask import Blueprint, jsonify, request
from models.Track import Track
from models.TrackSection import track_section
from sqlalchemy import create_engine
from sqlalchemy.sql import text
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = f"sqlite:///{os.path.abspath('server/db/track.db')}"
engine = create_engine(DATABASE_URL, echo=True)
Session = sessionmaker(bind=engine)

track_blueprint = Blueprint('track_routes', __name__)

@track_blueprint.route('/', methods=['GET'])
def get_tracks():
    session = Session()
    tracks = session.query(Track).all()

    track_list = []
    for track in tracks:
        sections_query = text("""
            SELECT section.sectionID, section.usageFee, section.length, section.maxSpeed, section.trackGauge,
                   section.startStationID, section.endStationID
            FROM track_section
            JOIN section ON track_section.sectionID = section.sectionID
            WHERE track_section.trackID = :trackID
            ORDER BY track_section.sequence ASC
        """)
        sections = session.execute(sections_query, {"trackID": track.trackID}).fetchall()

        sections_list = []
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

            sections_list.append({
                "sectionID": section.sectionID,
                "usageFee": section.usageFee,
                "length": section.length,
                "maxSpeed": section.maxSpeed,
                "trackGauge": section.trackGauge,
                "startStationID": section.startStationID,
                "endStationID": section.endStationID,
                "warnings": warnings_list
            })

        track_list.append({
            'trackID': track.trackID,
            'trackName': track.trackName,
            'sections': sections_list
        })

    return jsonify(track_list)

@track_blueprint.route('/<int:track_id>', methods=['GET'])
def get_track_by_id(track_id):
    session = Session()
    track = session.query(Track).filter(Track.trackID == track_id).first()

    if not track:
        return jsonify({"message": f"Track mit ID {track_id} nicht gefunden"}), 404

    sections_query = text("""
        SELECT section.sectionID, section.usageFee, section.length, section.maxSpeed, section.trackGauge,
               section.startStationID, section.endStationID
        FROM track_section
        JOIN section ON track_section.sectionID = section.sectionID
        WHERE track_section.trackID = :trackID
        ORDER BY track_section.sequence ASC
    """)
    sections = session.execute(sections_query, {"trackID": track_id}).fetchall()

    sections_list = []
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

        sections_list.append({
            "sectionID": section.sectionID,
            "usageFee": section.usageFee,
            "length": section.length,
            "maxSpeed": section.maxSpeed,
            "trackGauge": section.trackGauge,
            "startStationID": section.startStationID,
            "endStationID": section.endStationID,
            "warnings": warnings_list
        })

    return jsonify({
        'trackID': track.trackID,
        'trackName': track.trackName,
        'sections': sections_list
    })

@track_blueprint.route('/', methods=['POST'])
def create_track():
    session = Session()
    data = request.get_json()
    new_track = Track()

    try:
        new_track.trackName = data['trackName']
        section_ids = data['sectionIDs']

        if not new_track.validate_section_sequence(section_ids, session):
            return jsonify({"message": "Die übergebenen Sections bilden keine gültige Strecke"}), 400

        session.add(new_track)
        session.commit()

        for index, section_id in enumerate(section_ids):
            session.execute(track_section.insert().values(
                trackID=new_track.trackID,
                sectionID=section_id,
                sequence=index
            ))

        session.commit()
    except ValueError as e:
        session.rollback()
        return jsonify({"message": str(e)}), 400

    return jsonify({
        'trackID': new_track.trackID,
        'trackName': new_track.trackName,
        'sectionIDs': section_ids
    }), 201

@track_blueprint.route('/<int:track_id>', methods=['PUT'])
def update_track(track_id):
    session = Session()
    track = session.query(Track).filter(Track.trackID == track_id).first()

    if not track:
        return jsonify({"message": f"Track mit ID {track_id} nicht gefunden"}), 404

    data = request.get_json()

    try:
        if 'trackName' in data:
            track.trackName = data['trackName']

        if 'sectionIDs' in data:
            section_ids = data['sectionIDs']

            if not track.validate_section_sequence(section_ids, session):
                return jsonify({"message": "Die Reihenfolge der Sections ist ungültig"}), 400

            session.execute(track_section.delete().where(track_section.c.trackID == track.trackID))

            for index, section_id in enumerate(section_ids):
                session.execute(track_section.insert().values(
                    trackID=track.trackID,
                    sectionID=section_id,
                    sequence=index
                ))

        session.commit()
    except ValueError as e:
        session.rollback()
        return jsonify({"message": str(e)}), 400

    return jsonify({
        'trackID': track.trackID,
        'trackName': track.trackName,
        'sectionIDs': data.get('sectionIDs', [])
    }), 200

@track_blueprint.route('/<int:track_id>', methods=['DELETE'])
def delete_track(track_id):
    session = Session()
    track = session.query(Track).filter(Track.trackID == track_id).first()

    if not track:
        return jsonify({"message": f"Track mit ID {track_id} nicht gefunden"}), 404

    session.delete(track)
    session.commit()

    return jsonify({"message": f"Track mit ID {track_id} wurde erfolgreich gelöscht"}), 200