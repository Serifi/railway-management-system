import os
from flask import Blueprint, request, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, joinedload
from sqlalchemy.exc import IntegrityError
from models import Base, Train, TrainPassengerCars
from models.carriage import Railcar, PassengerCar, Carriage
from models.maintenance import Maintenance
from models.train import TrainPassengerCars
from math import fsum

train_blueprint = Blueprint('train_routes', __name__)

DATABASE_URL = f"sqlite:///{os.path.abspath('server/db/fleet.db')}"
engine = create_engine(DATABASE_URL, echo=False)
Session = sessionmaker(bind=engine)
Base.metadata.create_all(engine)

@train_blueprint.route('/', methods=['POST'])
def create_train():
    session = Session()
    try:
        data = request.get_json()
        if not data or 'name' not in data or 'railcarID' not in data or 'passengerCars' not in data:
            return jsonify({"message": "Required fields: name, railcarID, passengerCars"}), 400

        railcar = session.query(Railcar).filter_by(carriageID=data['railcarID']).first()
        if not railcar:
            return jsonify({"message": "Invalid railcarID"}), 404

        # Check if railcar is free
        if session.query(Train).filter_by(railcarID=data['railcarID']).first():
            return jsonify({"message": "This Railcar is already assigned"}), 400

        # Check passenger cars exist
        passengerCars = data['passengerCars']  # list of {id, position}
        ids = [pc['id'] for pc in passengerCars]
        pc_objs = session.query(PassengerCar).filter(PassengerCar.carriageID.in_(ids)).all()
        if len(pc_objs) != len(ids):
            return jsonify({"message": "Some PassengerCar IDs invalid"}), 404

        # Check trackGauge matching
        railcar_gauge = railcar.carriage.trackGauge
        for pc in pc_objs:
            if pc.carriage.trackGauge != railcar_gauge:
                return jsonify({"message": "Track gauge mismatch"}), 400

        # Check tractive force vs total passengerCar weight
        total_weight = fsum(pc.maxWeight for pc in pc_objs)
        if total_weight > railcar.maxTractiveForce:
            return jsonify({"message": "Railcar too weak"}), 400

        new_t = Train(name=data['name'], railcarID=data['railcarID'])
        session.add(new_t)
        session.commit()

        # Insert passengerCars + position
        for pc in passengerCars:
            session.execute(
                TrainPassengerCars.insert().values(
                    trainID=new_t.trainID,
                    passengerCarID=pc['id'],
                    position=pc['position']
                )
            )
        session.commit()

        return jsonify({
            "trainID": new_t.trainID,
            "name": new_t.name,
            "railcarID": new_t.railcarID,
            "passengerCars": passengerCars
        }), 201
    except IntegrityError:
        session.rollback()
        return jsonify({"message": "DB error: duplicate or invalid"}), 400
    finally:
        session.close()

@train_blueprint.route('/', methods=['GET'])
def get_trains():
    session = Session()
    try:
        trains = session.query(Train).options(
            joinedload(Train.railcar),
            joinedload(Train.passenger_cars)
        ).all()

        output = []
        for t in trains:
            # get positions from association
            assoc_rows = session.query(TrainPassengerCars).filter_by(trainID=t.trainID).all()
            pass_cars = []
            for row in assoc_rows:
                pass_cars.append({"id": row.passengerCarID, "position": row.position})
            output.append({
                "trainID": t.trainID,
                "name": t.name,
                "railcarID": t.railcarID,
                "passengerCars": pass_cars
            })
        return jsonify(output), 200
    finally:
        session.close()

@train_blueprint.route('/<int:trainID>', methods=['GET'])
def get_train_by_id(trainID):
    session = Session()
    try:
        t = session.query(Train).options(
            joinedload(Train.railcar),
            joinedload(Train.passenger_cars)
        ).filter_by(trainID=trainID).first()
        if not t:
            return jsonify({"message": "Train not found"}), 404

        assoc_rows = session.query(TrainPassengerCars).filter_by(trainID=trainID).all()
        pass_cars = []
        for row in assoc_rows:
            pass_cars.append({"id": row.passengerCarID, "position": row.position})

        return jsonify({
            "trainID": t.trainID,
            "name": t.name,
            "railcarID": t.railcarID,
            "passengerCars": pass_cars
        }), 200
    finally:
        session.close()

@train_blueprint.route('/<int:trainID>', methods=['PUT'])
def update_train(trainID):
    session = Session()
    try:
        data = request.get_json()
        t = session.query(Train).filter_by(trainID=trainID).first()
        if not t:
            return jsonify({"message": "Train not found"}), 404

        # Update name
        if 'name' in data and data['name'].strip():
            t.name = data['name'].strip()

        # Update railcar if provided
        if 'railcarID' in data:
            new_rc_id = data['railcarID']
            if new_rc_id != t.railcarID:
                rc_obj = session.query(Railcar).filter_by(carriageID=new_rc_id).first()
                if not rc_obj:
                    return jsonify({"message": "New Railcar does not exist"}), 404
                if session.query(Train).filter_by(railcarID=new_rc_id).first():
                    return jsonify({"message": "Railcar already in use"}), 400

                # Check gauge among current passengerCars
                gauge_rc = rc_obj.carriage.trackGauge
                assoc_pc = session.query(TrainPassengerCars).filter_by(trainID=trainID).all()
                pc_objs = session.query(PassengerCar).filter(PassengerCar.carriageID.in_([row.passengerCarID for row in assoc_pc])).all()
                for pc in pc_objs:
                    if pc.carriage.trackGauge != gauge_rc:
                        return jsonify({"message": "Track gauge mismatch"}), 400
                # Check force
                total_weight = fsum(pc.maxWeight for pc in pc_objs)
                if total_weight > rc_obj.maxTractiveForce:
                    return jsonify({"message": "Railcar too weak"}), 400
                t.railcarID = new_rc_id

        # Update passengerCars if provided
        if 'passengerCars' in data:
            # Clear old
            session.query(TrainPassengerCars).filter_by(trainID=trainID).delete()
            session.commit()
            # Validate new PCs
            new_pcs = data['passengerCars']
            pc_ids = [pc['id'] for pc in new_pcs]
            pc_objs = session.query(PassengerCar).filter(PassengerCar.carriageID.in_(pc_ids)).all()
            if len(pc_objs) != len(pc_ids):
                return jsonify({"message": "Some PassengerCar IDs invalid"}), 404

            # Check gauge
            railcar_obj = session.query(Railcar).filter_by(carriageID=t.railcarID).first()
            gauge_rc = railcar_obj.carriage.trackGauge
            for pc in pc_objs:
                if pc.carriage.trackGauge != gauge_rc:
                    return jsonify({"message": "Track gauge mismatch"}), 400

            # Check force
            total_weight = fsum(pc.maxWeight for pc in pc_objs)
            if total_weight > railcar_obj.maxTractiveForce:
                return jsonify({"message": "Railcar too weak"}), 400

            # Insert
            for pc in new_pcs:
                session.execute(
                    TrainPassengerCars.insert().values(
                        trainID=trainID,
                        passengerCarID=pc['id'],
                        position=pc['position']
                    )
                )

        session.commit()
        return jsonify({"message": "Train updated"}), 200
    except IntegrityError:
        session.rollback()
        return jsonify({"message": "DB error"}), 400
    finally:
        session.close()

@train_blueprint.route('/<int:trainID>', methods=['DELETE'])
def delete_train(trainID):
    session = Session()
    try:
        t = session.query(Train).filter_by(trainID=trainID).first()
        if not t:
            return jsonify({"message": "Train not found"}), 404

        # Check if there's maintenance
        maint = session.query(Maintenance).filter_by(trainID=trainID).first()
        if maint:
            return jsonify({"message": "Cannot delete train with existing maintenance"}), 400

        session.delete(t)
        session.commit()
        return jsonify({"message": "Train deleted"}), 200
    except IntegrityError:
        session.rollback()
        return jsonify({"message": "Error deleting train"}), 400
    finally:
        session.close()
