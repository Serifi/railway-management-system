import traceback
from datetime import datetime, timedelta, time
from zoneinfo import ZoneInfo

from flask import render_template, request, jsonify
import requests

from app.models import Stopplan, Track, TrainStation, RideExecution, Employee, Train
from app import app, db
from flask_cors import CORS, cross_origin
CORS(app)

@app.route('/stopplans')
def get_aLl_stopplans():
    stopplans = Stopplan.query.all()
    stopplan_list = []
    for stopplan in stopplans:
        trainStation_list = []
        for trainStation in stopplan.trainStations:
            trainStation_list.append({
                'id': trainStation.id,
                'name': trainStation.name,
                'address': trainStation.address
            })
        rideExecution_list = []
        for ride_execution in stopplan.rideExecutions:
            employee_list = []
            for employee in ride_execution.employees:
                employee_list.append({
                    'ssn': employee.ssn,
                    'firstName': employee.firstName,
                    'lastName': employee.lastName,
                    'password': employee.password,
                    'department': employee.department.value,
                    'role': employee.role.value,
                    'username': employee.username
                })
            rideExecution_list.append({
                'id': ride_execution.id,
                'price': ride_execution.price,
                'isCanceled': ride_execution.isCanceled,
                'delay': ride_execution.delay,
                'date': ride_execution.date.strftime('%d.%m.%Y'),  # Formatierte 'date' als String
                'time': ride_execution.time.strftime('%H:%M'),  # Formatierte 'time' als String
                'stopplanID': ride_execution.stopplanID,
                'train': {
                    'id': ride_execution.train.id,
                    'name': ride_execution.train.name
                },
                'employees': employee_list
            })
        stopplan_list.append({
            'id': stopplan.id,
            'name': stopplan.name,
            'minPrice': stopplan.minPrice,
            'trackID': stopplan.trackID,
            'trainStations': trainStation_list,
            'rideExecutions': rideExecution_list
        })
    return jsonify(stopplan_list)

@app.route('/stopplan/<int:stopplan_id>')
def get_stopplan(stopplan_id):

    stopplan = Stopplan.query.get_or_404(stopplan_id)
    trainStation_list = []
    for trainStation in stopplan.trainStations:
        trainStation_list.append({
            'id': trainStation.id,
            'name': trainStation.name,
            'address': trainStation.address
        })
    stopplan2 = {
        'id': stopplan.id,
        'name': stopplan.name,
        'minPrice': stopplan.minPrice,
        'trackID': stopplan.trackID,
        'trainStations': trainStation_list
    }
    return jsonify(stopplan2)

@app.route('/stopplan/<int:stopplanID>', methods=['DELETE'])
def deleteStopplan(stopplanID):
    stopplan = Stopplan.query.get_or_404(stopplanID)
    #if not stopplan.rideExecutions:
    db.session.delete(stopplan)
    db.session.commit()
    return jsonify({'message': 'Stopplan deleted'}), 200
    #else:
        #return jsonify({'message': 'Stopplan is used'}), 200


@app.route('/create_stopplan/', methods=['POST'])
def createStopplan():
    try:
        data = request.get_json()

        if not data.get('name') or not data.get('trackID'):
            return jsonify({'message': 'Fehlende Daten: name oder trackID'}), 400

        track = Track.query.get(data['trackID'])
        if not track:
            return jsonify({'message': 'Track mit der angegebenen trackID existiert nicht'}), 404


        minPrice = 0
        for section in track.sections:
            print(f"Section ID: {section.id}, usageFee: {section.usageFee}")
            minPrice += section.usageFee
        minPrice = minPrice / len(track.sections)

        train_stations = []
        if 'trainStations' in data:
            for station_data in data['trainStations']:
                station = TrainStation.query.get(station_data['id'])
                if station:
                    train_stations.append(station)

        stopplan = Stopplan(
            name=data['name'],
            minPrice=minPrice,
            trackID=data['trackID'],
            trainStations=train_stations
        )

        db.session.add(stopplan)
        db.session.commit()

        return jsonify({
            'id': stopplan.id,
            'name': stopplan.name,
            'minPrice': stopplan.minPrice,
            'trackID': stopplan.trackID,
            'trainStations': [{'id': station.id, 'name': station.name, 'address': station.address} for station in stopplan.trainStations]
        }), 201

    except Exception as e:
        return jsonify({'message': f'Fehler beim Erstellen des Stopplans: {str(e)}'}), 500



@app.route('/stopplan/<int:stopplan_id>', methods=['PUT'])
def update_stopplan(stopplan_id):
    try:
        data = request.get_json()

        stopplan = Stopplan.query.get(stopplan_id)
        if not stopplan:
            return jsonify({'message': 'Stopplan nicht gefunden'}), 404


        if 'name' in data:
            stopplan.name = data['name']
        if 'trackID' in data:
            track = Track.query.get(data['trackID'])
            if not track:
                return jsonify({'message': 'Track mit der angegebenen trackID existiert nicht'}), 404
            stopplan.trackID = data['trackID']


        if 'trainStations' in data:
            new_train_stations = []
            for station_data in data['trainStations']:
                station = TrainStation.query.get(station_data['id'])
                if station:
                    new_train_stations.append(station)
            stopplan.trainStations = new_train_stations

        minPrice = 0
        for section in track.sections:
            print(f"Section ID: {section.id}, usageFee: {section.usageFee}")
            minPrice += section.usageFee
        minPrice = minPrice / len(track.sections)

        stopplan.minPrice = minPrice

        db.session.commit()


        return jsonify({
            'id': stopplan.id,
            'name': stopplan.name,
            'minPrice': stopplan.minPrice,
            'trackID': stopplan.trackID,
            'trainStations': [{'id': station.id, 'name': station.name, 'address': station.address} for station in stopplan.trainStations]
        }), 200

    except Exception as e:
        return jsonify({'message': f'Fehler beim Aktualisieren des Stopplans: {str(e)}'}), 500

@app.route('/create_ride_execution/', methods=['POST'])
def create_ride_execution():
    try:
        data = request.get_json()


        employee_list = []
        if 'employeeSSN_list' in data:
            for employee_data in data['employeeSSN_list']:
                employee = Employee.query.get(employee_data['ssn'])
                if employee:
                    employee_list.append(employee)
                else:
                    return jsonify({'message': f'Mitarbeiter mit SSN {employee_data["ssn"]} nicht gefunden'}), 400
        else:
            return jsonify({'message': 'No employeeSSN_list found in data'}), 400

        try:
            start_date_obj = datetime.strptime(data['startDate'][:10], '%Y-%m-%d').date()
            start_date_obj += timedelta(days=1)
        except ValueError:
            return jsonify({'message': 'Ungültiges Startdatum. Format sollte YYYY-MM-DD sein.'}), 400
        if data['endDate']:
            end_date_obj = datetime.strptime(data['endDate'][:10], '%Y-%m-%d').date()

        if data['selectedDays']:
            selected_days = data['selectedDays']
            weekdays = [day['value'] for day in selected_days]



        # Initialdaten und Konfiguration
        if data['zeitIntervall']:
            zeitIntervall = data['zeitIntervall']  # Intervall in Minuten

        # Startzeit und Endzeit in datetime-Objekte konvertieren
        utc_time = datetime.strptime(data['startTime'], '%Y-%m-%dT%H:%M:%S.%fZ')  # Startzeit im UTC-Format
        utc_time = utc_time.replace(tzinfo=ZoneInfo("UTC"))  # Zeit als UTC markieren
        local_timezone = ZoneInfo('Europe/Berlin')  # Lokale Zeitzone
        local_start_datetime = utc_time.astimezone(local_timezone).replace(microsecond=0)  # Lokale Zeit konvertieren

        if data['endTime']:
            utc_time2 = datetime.strptime(data['endTime'], '%Y-%m-%dT%H:%M:%S.%fZ')  # Endzeit im UTC-Format
            utc_time2 = utc_time2.replace(tzinfo=ZoneInfo("UTC"))  # Zeit als UTC markieren
            local_end_datetime = utc_time2.astimezone(local_timezone).replace(microsecond=0)  # Lokale Zeit konvertieren

        # Zeit- und Datumslogik
        current_date = start_date_obj  # Startdatum
        rideExecution_list = []

######################################
        if data['datumIsEinmalig'] == True and data['zeitIsEinmalig'] == True:
            ride_execution = RideExecution(
                price= data['price'],
                isCanceled=False,
                delay=0,
                date=start_date_obj,  # Nur das Datum speichern
                time=local_start_datetime.time(),  # Nur die Zeit speichern
                stopplanID=data['stopplanID'],
                trainID=data['trainID'],
                employees=employee_list
            )
            db.session.add(ride_execution)
            rideExecution_list.append(ride_execution)
            db.session.commit()
######################################
        elif data['datumIsEinmalig'] == True and data['zeitIsEinmalig'] == False:
            current_time = datetime.combine(start_date_obj, local_start_datetime.time())
            end_time = datetime.combine(start_date_obj, local_end_datetime.time())

            while current_time <= end_time:
                ride_execution = RideExecution(
                    price= data['price'],
                    isCanceled=False,
                    delay=0,
                    date=start_date_obj,  # Nur das Datum speichern
                    time=current_time.time(),  # Nur die Zeit speichern
                    stopplanID=data['stopplanID'],
                    trainID=data['trainID'],
                    employees=employee_list
                )
                db.session.add(ride_execution)
                rideExecution_list.append(ride_execution)
                current_time += timedelta(minutes=zeitIntervall)
            db.session.commit()
######################################
        elif data['datumIsEinmalig'] == False and data['zeitIsEinmalig'] == True:
            while current_date <= end_date_obj:
                if current_date.isoweekday() in weekdays:  # Überprüfen, ob der Tag ein gültiger Wochentag ist
                    ride_execution = RideExecution(
                        price= data['price'],
                        isCanceled=False,
                        delay=0,
                        date=current_date,  # Nur das Datum speichern
                        time=local_start_datetime.time(),  # Nur die Zeit speichern
                        stopplanID=data['stopplanID'],
                        trainID=data['trainID'],
                        employees=employee_list
                    )
                    db.session.add(ride_execution)
                    rideExecution_list.append(ride_execution)

                current_date += timedelta(days=1)
            db.session.commit()

######################################
        elif data['datumIsEinmalig'] == False and data['zeitIsEinmalig'] == False:
            while current_date <= end_date_obj:
                if current_date.isoweekday() in weekdays:  # Überprüfen, ob der Tag ein gültiger Wochentag ist
                    # Setze die aktuelle Zeit für diesen Tag
                    current_time = datetime.combine(current_date, local_start_datetime.time())
                    end_time = datetime.combine(current_date, local_end_datetime.time())

                    while current_time <= end_time:
                        # Fahrt erstellen
                        ride_execution = RideExecution(
                            price= data['price'],
                            isCanceled=False,
                            delay=0,
                            date=current_date,  # Nur das Datum speichern
                            time=current_time.time(),  # Nur die Zeit speichern
                            stopplanID=data['stopplanID'],
                            trainID=data['trainID'],
                            employees=employee_list
                        )
                        db.session.add(ride_execution)
                        rideExecution_list.append(ride_execution)
                        # Zeit um Intervall erhöhen
                        current_time += timedelta(minutes=zeitIntervall)

                # Nächster Tag
                current_date += timedelta(days=1)

            # Änderungen in der Datenbank speichern
            db.session.commit()
#########################
        return jsonify(
            [{
            'id': ride_execution.id,
            'price': ride_execution.price,
            'isCanceled': ride_execution.isCanceled,
            'delay': ride_execution.delay,
            'date': ride_execution.date.strftime('%d.%m.%Y'),  # Formatierte 'date' als String
            'time': ride_execution.time.strftime('%H:%M'),  # Formatierte 'time' als String
            'stopplanID': ride_execution.stopplanID,
            'train': {
                'id': ride_execution.train.name,
                'name': ride_execution.train.name,
            },
            'employees': [{
                'ssn': employee.ssn,
                'firstName': employee.firstName,
                'lastName': employee.lastName,
                'password': employee.password,
                'department': employee.department.value,
                'role': employee.role.value,
                'username': employee.username
            } for employee in ride_execution.employees]
        }for ride_execution in rideExecution_list]), 201

    except Exception as e:
        traceback.print_exc()
        return jsonify({'message': f'Fehler beim Erstellen der Fahrdurchführung: {str(e)}'}), 500






@app.route('/available_trains', methods=['POST'])
def get_available_trains():
    try:
        data = request.get_json()

        # Verfügbare Züge
        all_trains = Train.query.all()
        unavailable_trains = set()

        # Datum und Zeitobjekte vorbereiten
        start_date_obj = datetime.strptime(data['startDate'][:10], '%Y-%m-%d').date()
        start_date_obj += timedelta(days=1)

        if data['endDate']:
            end_date_obj = datetime.strptime(data['endDate'][:10], '%Y-%m-%d').date()

        # Zeitkonvertierung
        local_timezone = ZoneInfo('Europe/Berlin')
        utc_time = datetime.strptime(data['startTime'], '%Y-%m-%dT%H:%M:%S.%fZ').replace(tzinfo=ZoneInfo("UTC"))
        local_start_datetime = utc_time.astimezone(local_timezone).replace(microsecond=0)  # Millisekunden entfernen

        if data['endTime']:
            utc_time2 = datetime.strptime(data['endTime'], '%Y-%m-%dT%H:%M:%S.%fZ').replace(tzinfo=ZoneInfo("UTC"))
            local_end_datetime = utc_time2.astimezone(local_timezone).replace(microsecond=0)  # Millisekunden entfernen

        # Wochen- und Zeitlogik
        weekdays = [day['value'] for day in data['selectedDays']] if data['selectedDays'] else []
        zeitIntervall = data['zeitIntervall'] if data['zeitIntervall'] else 0

        def round_to_minute(t: time):
            return t.replace(second=0, microsecond=0)

        local_start_time_rounded = round_to_minute(local_start_datetime.time())


        # 1. Datum und Zeit einmalig
        if data['datumIsEinmalig'] and data['zeitIsEinmalig']:
            ride_executions = RideExecution.query.filter_by(
                date=start_date_obj,
                time=local_start_time_rounded  # Zeit ohne Millisekunden
            ).all()
            unavailable_trains.update([execution.trainID for execution in ride_executions])

            print("Local start datetime time:", local_start_time_rounded)
            for execution in RideExecution.query.filter_by(date=start_date_obj).all():
                print("DB time:", execution.time)
                print("Match:", execution.time == local_start_datetime.time())

        # 2. Datum und Zeit im Intervall
        elif not data['datumIsEinmalig'] and not data['zeitIsEinmalig']:
            current_date = start_date_obj
            while current_date <= end_date_obj:
                if current_date.isoweekday() in weekdays:
                    current_time = datetime.combine(current_date, local_start_datetime.time())
                    end_time = datetime.combine(current_date, local_end_datetime.time())

                    while current_time <= end_time:
                        rounded_time = current_time.time().replace(second=0, microsecond=0)

                        executions = RideExecution.query.filter_by(
                            date=current_date,
                            time=rounded_time
                        ).all()

                        unavailable_trains.update([execution.trainID for execution in executions])
                        current_time += timedelta(minutes=zeitIntervall)

                current_date += timedelta(days=1)


        # 3. Datum einmalig, Zeit im Intervall
        elif data['datumIsEinmalig'] and not data['zeitIsEinmalig']:
            current_time = datetime.combine(start_date_obj, local_start_datetime.time())
            end_time = datetime.combine(start_date_obj, local_end_datetime.time())

            while current_time <= end_time:
                rounded_time = current_time.time().replace(second=0, microsecond=0)

                executions = RideExecution.query.filter_by(
                    date=start_date_obj,
                    time=rounded_time
                ).all()

                # IDs der belegten Züge sammeln
                unavailable_trains.update([execution.trainID for execution in executions])
                current_time += timedelta(minutes=zeitIntervall)


        # 4. Datum im Intervall, Zeit einmalig
        elif not data['datumIsEinmalig'] and data['zeitIsEinmalig']:
            current_date = start_date_obj
            while current_date <= end_date_obj:
                if current_date.isoweekday() in weekdays:
                    rounded_time = local_start_datetime.time().replace(second=0, microsecond=0)

                    executions = RideExecution.query.filter_by(
                        date=current_date,
                        time=rounded_time
                    ).all()
                    unavailable_trains.update([execution.trainID for execution in executions])

                current_date += timedelta(days=1)

        # Verfügbare Züge berechnen
        available_trains = [
            {'id': train.id, 'name': train.name}
            for train in all_trains if train.id not in unavailable_trains
        ]

        return jsonify(available_trains), 200

    except Exception as e:
        traceback.print_exc()
        return jsonify({'message': f'Fehler beim Abrufen der verfügbaren Züge: {str(e)}'}), 500






@app.route("/trains")
def get_all_trains():
    trains = Train.query.all()
    train_list = []
    for train in trains:
        train_list.append({
            'id': train.id,
            'name': train.name,
        })
    return jsonify(train_list)












@app.route('/ride_executions')
def get_all_ride_executions():
    ride_executions = RideExecution.query.all()
    ride_executions_list = []

    for ride_execution in ride_executions:
        employee_list = []
        for employee in ride_execution.employees:
            employee_list.append({
                'ssn': employee.ssn,
                'firstName': employee.firstName,
                'lastName': employee.lastName,
                'password': employee.password,
                'department': employee.department.value,
                'role': employee.role.value,
                'username': employee.username
            })
        ride_executions_list.append({
            'id': ride_execution.id,
            'price': ride_execution.price,
            'isCanceled': ride_execution.isCanceled,
            'delay': ride_execution.delay,
            'date': ride_execution.date.strftime('%d.%m.%Y'),  # Formatierte 'date' als String
            'time': ride_execution.time.strftime('%H:%M'),  # Formatierte 'time' als String
            'stopplanID': ride_execution.stopplanID,
            'train': {
                'id': ride_execution.train.id,
                'name': ride_execution.train.name
            },
            'employees': employee_list
        })
    return jsonify(ride_executions_list)


@app.route('/ride_execution/<int:ride_execution_id>', methods=['DELETE'])
def delete_ride_execution(ride_execution_id):
    ride_execution = RideExecution.query.get_or_404(ride_execution_id)
    db.session.delete(ride_execution)
    db.session.commit()
    return jsonify({'message': 'Ride_Execution deleted'}), 200


@app.route('/ride_execution/<int:ride_execution_id>', methods=['PUT'])
def update_ride_execution(ride_execution_id):
    ride_execution = RideExecution.query.get(ride_execution_id)
    if not ride_execution:
        return jsonify({"error": "RideExecution not found"}), 404

    data = request.get_json()

    if 'isCanceled' in data:
        if data['isCanceled'] == "Ja":
            ride_execution.isCanceled = True
            ride_execution.delay = 0
        else:
            ride_execution.isCanceled = False


    if 'delay' in data:
        ride_execution.delay = data['delay']


    try:
        db.session.commit()
        return jsonify({
            "message": "RideExecution updated successfully",
            "rideExecution": {
                'id': ride_execution.id,
            'price': ride_execution.price,
            'isCanceled': ride_execution.isCanceled,
            'delay': ride_execution.delay,
            'stopplanID': ride_execution.stopplanID,
            'train': {
                'id': ride_execution.train.id,
                'name': ride_execution.train.name
            }

            }
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Update failed: {str(e)}"}), 500





@app.route("/employees")
@cross_origin()
def get_all_employees():
    employees = Employee.query.all()
    employee_list = []
    for employee in employees:
        rideExecution_list = []
        for ride_execution in employee.rideExecutions:
            rideExecution_list.append({
                'id': ride_execution.id,
                'price': ride_execution.price,
                'isCanceled': ride_execution.isCanceled,
                'delay': ride_execution.delay,
                'date': ride_execution.date.strftime('%d.%m.%Y'),  # Formatierte 'date' als String
                'time': ride_execution.time.strftime('%H:%M'),  # Formatierte 'time' als String
                'stopplan': {
                    'name': ride_execution.stopplan.name,
                },
                'train': {
                    'id': ride_execution.train.id,
                    'name': ride_execution.train.name
                },
            })
        employee_list.append({
            'ssn': employee.ssn,
            'firstName': employee.firstName,
            'lastName': employee.lastName,
            'password': employee.password,
            'department': employee.department.value,
            'role': employee.role.value,
            'username': employee.username,
            'rideExecutions': rideExecution_list
        })
    return (jsonify(employee_list))