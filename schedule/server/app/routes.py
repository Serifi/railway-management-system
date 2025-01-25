import traceback
from datetime import datetime, timedelta, time
from zoneinfo import ZoneInfo

from flask import render_template, request, jsonify
import requests

from app.models import Stopplan, Track, TrainStation, RideExecution, Employee
from app import app, db
from flask_cors import CORS, cross_origin

CORS(app)

@app.route('/stopplans')
def get_aLl_stopplans():
    # Alle Stoppläne aus der Datenbank abrufen
    stopplans = Stopplan.query.all()
    stopplan_list = []  # Liste zum Speichern der Stoppläne

    for stopplan in stopplans:
        # Bahnhöfe des aktuellen Stopplans sammeln
        trainStation_list = []
        for trainStation in stopplan.trainStations:
            trainStation_list.append({
                'id': trainStation.id,
                'name': trainStation.name,
                'address': trainStation.address
            })

        # Fahrtausführungen des Stopplans sammeln
        rideExecution_list = []
        for ride_execution in stopplan.rideExecutions:
            # Mitarbeiter der jeweiligen Fahrtausführung sammeln
            employee_list = []
            for employee in ride_execution.employees:
                employee_list.append({
                    'ssn': employee.ssn,
                    'firstName': employee.firstName,
                    'lastName': employee.lastName,
                    'password': employee.password,  # Sicherheitsrisiko: Passwörter sollten nicht ausgegeben werden
                    'department': employee.department.value,
                    'role': employee.role.value,
                    'username': employee.username
                })
            # Fahrtausführung zur Liste hinzufügen
            rideExecution_list.append({
                'id': ride_execution.id,
                'price': ride_execution.price,
                'isCanceled': ride_execution.isCanceled,
                'delay': ride_execution.delay,
                'date': ride_execution.date.strftime('%d.%m.%Y'),  # Datum formatieren
                'time': ride_execution.time.strftime('%H:%M'),  # Zeit formatieren
                'stopplanID': ride_execution.stopplanID,
                'trainID': ride_execution.trainID,
                'employees': employee_list
            })

        # Stopplan-Daten zur Liste hinzufügen
        stopplan_list.append({
            'id': stopplan.id,
            'name': stopplan.name,
            'minPrice': stopplan.minPrice,
            'trackID': stopplan.trackID,
            'trainStations': trainStation_list,
            'rideExecutions': rideExecution_list
        })
    return jsonify(stopplan_list)  # Liste als JSON zurückgeben

@app.route('/stopplan/<int:stopplan_id>')
def get_stopplan(stopplan_id):
    # Einzelnen Stopplan anhand der ID abrufen
    stopplan = Stopplan.query.get_or_404(stopplan_id)

    # Bahnhöfe des Stopplans sammeln
    trainStation_list = []
    for trainStation in stopplan.trainStations:
        trainStation_list.append({
            'id': trainStation.id,
            'name': trainStation.name,
            'address': trainStation.address
        })

    # Stopplan-Daten als JSON zurückgeben
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
    # Stopplan anhand der ID löschen
    stopplan = Stopplan.query.get_or_404(stopplanID)
    db.session.delete(stopplan)  # Stopplan aus der Datenbank entfernen
    db.session.commit()  # Änderungen speichern
    return jsonify({'message': 'Stopplan deleted'}), 200


@app.route('/create_stopplan/', methods=['POST'])
def createStopplan():
    try:
        # JSON-Daten aus der Anfrage abrufen
        data = request.get_json()

        # Überprüfen, ob die erforderlichen Felder vorhanden sind
        if not data.get('name') or not data.get('trackID'):
            return jsonify({'message': 'Fehlende Daten: name oder trackID'}), 400

        # API-Endpoint aufrufen, um die Strecke anhand der trackID zu erhalten
        response = requests.get(f'http://127.0.0.1:5001/track/tracks/{data["trackID"]}')

        # Überprüfen, ob die Strecke gefunden wurde
        if response.status_code != 200:
            return jsonify({'message': 'Fehler beim Abrufen der Strecke'}), response.status_code

        track = response.json()  # JSON-Daten der Strecke

        # Mindestpreis basierend auf den Abschnitten der Strecke berechnen
        minPrice = 0
        for section in track['sections']:
            # Abschnittsinformationen aus dem Dictionary extrahieren
            sectionID = section['sectionID']
            usageFee = section['usageFee']
            print(f"Section ID: {sectionID}, usageFee: {usageFee}")
            minPrice += usageFee

        if len(track['sections']) > 0:
            minPrice = minPrice / len(track['sections'])  # Durchschnitt der Gebühren berechnen

        # Bahnhöfe aus den übergebenen Daten abrufen
        train_stations = []
        if 'trainStations' in data:
            for station_data in data['trainStations']:
                station = TrainStation.query.get(station_data['id'])
                if station:
                    train_stations.append(station)

        # Neuen Stopplan erstellen
        stopplan = Stopplan(
            name=data['name'],
            minPrice=minPrice,
            trackID=data['trackID'],
            trainStations=train_stations
        )

        # Stopplan in die Datenbank einfügen
        db.session.add(stopplan)
        db.session.commit()

        # Erfolgreich erstellten Stopplan zurückgeben
        return jsonify({
            'id': stopplan.id,
            'name': stopplan.name,
            'minPrice': stopplan.minPrice,
            'trackID': stopplan.trackID,
            'trainStations': [{'id': station.id, 'name': station.name, 'address': station.address} for station in
                              stopplan.trainStations]
        }), 201

    except Exception as e:
        return jsonify({'message': f'Fehler beim Erstellen des Stopplans: {str(e)}'}), 500


@app.route('/stopplan/<int:stopplan_id>', methods=['PUT'])
def update_stopplan(stopplan_id):
    try:
        # Daten aus der Anfrage lesen
        data = request.get_json()

        # Stopplan aus der Datenbank holen, falls er existiert
        stopplan = Stopplan.query.get(stopplan_id)
        if not stopplan:
            return jsonify({'message': 'Stopplan nicht gefunden'}), 404

        # Stopplan-Name aktualisieren, falls in den Daten enthalten
        if 'name' in data:
            stopplan.name = data['name']
        # Track-ID aktualisieren und überprüfen, ob der Track existiert
        if 'trackID' in data:
            track = Track.query.get(data['trackID'])
            if not track:
                return jsonify({'message': 'Track mit der angegebenen trackID existiert nicht'}), 404
            stopplan.trackID = data['trackID']

        # Zugstationen aktualisieren, falls in den Daten enthalten
        if 'trainStations' in data:
            new_train_stations = []
            for station_data in data['trainStations']:
                station = TrainStation.query.get(station_data['id'])
                if station:
                    new_train_stations.append(station)
            stopplan.trainStations = new_train_stations

        # Berechnung des Mindestpreises basierend auf den Track-Sektionen
        minPrice = 0
        for section in track.sections:
            print(f"Section ID: {section.id}, usageFee: {section.usageFee}")
            minPrice += section.usageFee
        minPrice = minPrice / len(track.sections)

        # Mindestpreis im Stopplan speichern
        stopplan.minPrice = minPrice

        # Änderungen in der Datenbank speichern
        db.session.commit()

        # Aktualisierten Stopplan zurückgeben
        return jsonify({
            'id': stopplan.id,
            'name': stopplan.name,
            'minPrice': stopplan.minPrice,
            'trackID': stopplan.trackID,
            'trainStations': [{'id': station.id, 'name': station.name, 'address': station.address} for station in stopplan.trainStations]
        }), 200

    except Exception as e:
        # Fehlerbehandlung und Fehlermeldung zurückgeben
        return jsonify({'message': f'Fehler beim Aktualisieren des Stopplans: {str(e)}'}), 500

@app.route('/create_ride_execution/', methods=['POST'])
def create_ride_execution():
    try:
        # Daten aus der Anfrage lesen
        data = request.get_json()

        # Liste der Mitarbeiter erstellen
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

        # Start- und Enddatum verarbeiten
        try:
            start_date_obj = datetime.strptime(data['startDate'][:10], '%Y-%m-%d').date()
            start_date_obj += timedelta(days=1)  # Ein Tag hinzufügen
        except ValueError:
            return jsonify({'message': 'Ungültiges Startdatum. Format sollte YYYY-MM-DD sein.'}), 400
        if data['endDate']:
            end_date_obj = datetime.strptime(data['endDate'][:10], '%Y-%m-%d').date()

        # Wochentage für wiederkehrende Fahrten
        if data['selectedDays']:
            selected_days = data['selectedDays']
            weekdays = [day['value'] for day in selected_days]

        # Zeitintervall verarbeiten
        if data['zeitIntervall']:
            zeitIntervall = data['zeitIntervall']

        # Start- und Endzeit in lokale Zeit umrechnen
        utc_time = datetime.strptime(data['startTime'], '%Y-%m-%dT%H:%M:%S.%fZ').replace(tzinfo=ZoneInfo("UTC"))
        local_timezone = ZoneInfo('Europe/Berlin')
        local_start_datetime = utc_time.astimezone(local_timezone).replace(second=0, microsecond=0)
        if data['endTime']:
            utc_time2 = datetime.strptime(data['endTime'], '%Y-%m-%dT%H:%M:%S.%fZ').replace(tzinfo=ZoneInfo("UTC"))
            local_end_datetime = utc_time2.astimezone(local_timezone).replace(second=0, microsecond=0)

        # Listen für Fahrtdurchführungen erstellen
        current_date = start_date_obj
        rideExecution_list = []

        # Szenarien basierend auf Einmaligkeit von Datum und Zeit
        if data['datumIsEinmalig'] == True and data['zeitIsEinmalig'] == True:
            # Einmalige Fahrt erstellen
            ride_execution = RideExecution(
                price=data['price'],
                isCanceled=False,
                delay=0,
                date=start_date_obj,
                time=local_start_datetime.time(),
                stopplanID=data['stopplanID'],
                trainID=data['trainID'],
                employees=employee_list
            )
            db.session.add(ride_execution)
            rideExecution_list.append(ride_execution)
            db.session.commit()

        elif data['datumIsEinmalig'] == True and data['zeitIsEinmalig'] == False:
            # Mehrere Fahrten an einem Tag erstellen
            current_time = datetime.combine(start_date_obj, local_start_datetime.time())
            end_time = datetime.combine(start_date_obj, local_end_datetime.time())

            while current_time <= end_time:
                ride_execution = RideExecution(
                    price=data['price'],
                    isCanceled=False,
                    delay=0,
                    date=start_date_obj,
                    time=current_time.time(),
                    stopplanID=data['stopplanID'],
                    trainID=data['trainID'],
                    employees=employee_list
                )
                db.session.add(ride_execution)
                rideExecution_list.append(ride_execution)
                current_time += timedelta(minutes=zeitIntervall)
            db.session.commit()

        elif data['datumIsEinmalig'] == False and data['zeitIsEinmalig'] == True:
            # Mehrere Tage mit einer Zeit erstellen
            while current_date <= end_date_obj:
                if current_date.isoweekday() in weekdays:
                    ride_execution = RideExecution(
                        price=data['price'],
                        isCanceled=False,
                        delay=0,
                        date=current_date,
                        time=local_start_datetime.time(),
                        stopplanID=data['stopplanID'],
                        trainID=data['trainID'],
                        employees=employee_list
                    )
                    db.session.add(ride_execution)
                    rideExecution_list.append(ride_execution)

                current_date += timedelta(days=1)
            db.session.commit()

        elif data['datumIsEinmalig'] == False and data['zeitIsEinmalig'] == False:
            # Wiederkehrende Fahrten mit Intervallen erstellen
            while current_date <= end_date_obj:
                if current_date.isoweekday() in weekdays:
                    current_time = datetime.combine(current_date, local_start_datetime.time())
                    end_time = datetime.combine(current_date, local_end_datetime.time())

                    while current_time <= end_time:
                        ride_execution = RideExecution(
                            price=data['price'],
                            isCanceled=False,
                            delay=0,
                            date=current_date,
                            time=current_time.time(),
                            stopplanID=data['stopplanID'],
                            trainID=data['trainID'],
                            employees=employee_list
                        )
                        db.session.add(ride_execution)
                        rideExecution_list.append(ride_execution)
                        current_time += timedelta(minutes=zeitIntervall)

                current_date += timedelta(days=1)

            db.session.commit()

        # Erfolgreiche Antwort mit erstellten Fahrten zurückgeben
        return jsonify([{
            'id': ride_execution.id,
            'price': ride_execution.price,
            'isCanceled': ride_execution.isCanceled,
            'delay': ride_execution.delay,
            'date': ride_execution.date.strftime('%d.%m.%Y'),
            'time': ride_execution.time.strftime('%H:%M'),
            'stopplanID': ride_execution.stopplanID,
            'trainID': ride_execution.trainID,
            'employees': [{
                'ssn': employee.ssn,
                'firstName': employee.firstName,
                'lastName': employee.lastName,
                'password': employee.password,
                'department': employee.department.value,
                'role': employee.role.value,
                'username': employee.username
            } for employee in ride_execution.employees]
        } for ride_execution in rideExecution_list]), 201

    except Exception as e:
        # Fehlerausgabe und Fehlermeldung zurückgeben
        traceback.print_exc()
        return jsonify({'message': f'Fehler beim Erstellen der Fahrdurchführung: {str(e)}'}), 500


@app.route('/available_trains', methods=['POST'])
def get_available_trains():
    try:
        data = request.get_json()  # JSON-Daten von der Anfrage abrufen

        # Alle Züge abrufen
        all_trains = get_all_trains()  # Sicherstellen, dass die Daten korrekt deserialisiert werden
        unavailable_trains = set()

        start_date_obj = datetime.strptime(data['startDate'][:10], '%Y-%m-%d').date()
        start_date_obj += timedelta(days=1)

        if data['endDate']:
            end_date_obj = datetime.strptime(data['endDate'][:10], '%Y-%m-%d').date()

        local_timezone = ZoneInfo('Europe/Berlin')
        utc_time = datetime.strptime(data['startTime'], '%Y-%m-%dT%H:%M:%S.%fZ').replace(tzinfo=ZoneInfo("UTC"))
        local_start_datetime = utc_time.astimezone(local_timezone).replace(second=0, microsecond=0)
        if data['endTime']:
            utc_time2 = datetime.strptime(data['endTime'], '%Y-%m-%dT%H:%M:%S.%fZ').replace(tzinfo=ZoneInfo("UTC"))
            local_end_datetime = utc_time2.astimezone(local_timezone).replace(second=0, microsecond=0)

        weekdays = [day['value'] for day in data['selectedDays']] if data['selectedDays'] else []
        zeitIntervall = data['zeitIntervall'] if data['zeitIntervall'] else 0

        def round_to_minute(t: time):
            return t.replace(second=0, microsecond=0)

        local_start_time_rounded = round_to_minute(local_start_datetime.time())

        # **Fall 1: Datum und Zeit einmalig**
        if data['datumIsEinmalig'] and data['zeitIsEinmalig']:
            ride_executions = RideExecution.query.filter_by(
                date=start_date_obj,
                time=local_start_time_rounded
            ).all()
            unavailable_trains.update([execution.trainID for execution in ride_executions])

        # **Fall 2: Datum und Zeit im Intervall**
        elif not data['datumIsEinmalig'] and not data['zeitIsEinmalig']:
            current_date = start_date_obj
            while current_date <= end_date_obj:  # Schleife durch alle Tage im Intervall
                if current_date.isoweekday() in weekdays:  # Nur ausgewählte Wochentage prüfen
                    current_time = datetime.combine(current_date, local_start_datetime.time())
                    end_time = datetime.combine(current_date, local_end_datetime.time())

                    while current_time <= end_time:  # Zeiten im Intervall prüfen
                        rounded_time = current_time.time().replace(second=0, microsecond=0)
                        executions = RideExecution.query.filter_by(
                            date=current_date,
                            time=rounded_time
                        ).all()
                        unavailable_trains.update([execution.trainID for execution in executions])
                        current_time += timedelta(minutes=zeitIntervall)  # Zeitintervall hinzufügen

                current_date += timedelta(days=1)

        # **Fall 3: Datum einmalig, Zeit im Intervall**
        elif data['datumIsEinmalig'] and not data['zeitIsEinmalig']:
            current_time = datetime.combine(start_date_obj, local_start_datetime.time())
            end_time = datetime.combine(start_date_obj, local_end_datetime.time())

            while current_time <= end_time:
                rounded_time = current_time.time().replace(second=0, microsecond=0)
                executions = RideExecution.query.filter_by(
                    date=start_date_obj,
                    time=rounded_time
                ).all()
                unavailable_trains.update([execution.trainID for execution in executions])
                current_time += timedelta(minutes=zeitIntervall)

        # **Fall 4: Datum im Intervall, Zeit einmalig**
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

        # Verfügbare Züge ermitteln, die nicht im Set der belegten Züge sind
        available_trains = [
            {'id': train['trainID'], 'name': train['name']}
            for train in all_trains if train['trainID'] not in unavailable_trains
        ]

        return jsonify(available_trains), 200  # Liste der verfügbaren Züge zurückgeben

    except Exception as e:
        print(f"Fehler aufgetreten: {str(e)}")
        traceback.print_exc()
        return jsonify({'message': f'Fehler beim Abrufen der verfügbaren Züge: {str(e)}'}), 500




def get_all_trains():
    # Anfrage an den Zug-Endpoint senden
    response = requests.get('http://127.0.0.1:5002/fleet/trains')

    # Überprüfen, ob die Anfrage erfolgreich war
    if response.status_code != 200:
        raise Exception(f"Fehler beim Abrufen der Züge: {response.status_code} - {response.text}")

    # JSON-Daten aus der Antwort extrahieren
    return response.json()


@app.route('/ride_executions')
def get_all_ride_executions():
    # Alle Fahrten aus der Datenbank abrufen
    ride_executions = RideExecution.query.all()
    ride_executions_list = []

    # Für jede Fahrt die relevanten Daten sammeln
    for ride_execution in ride_executions:
        employee_list = []
        # Liste der Mitarbeiter für jede Fahrt
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

        # Die Fahrtdaten zusammenstellen
        ride_executions_list.append({
            'id': ride_execution.id,
            'price': ride_execution.price,
            'isCanceled': ride_execution.isCanceled,
            'delay': ride_execution.delay,
            'date': ride_execution.date.strftime('%d.%m.%Y'),  # Datum im Format dd.MM.yyyy
            'time': ride_execution.time.strftime('%H:%M'),  # Uhrzeit im Format HH:mm
            'stopplanID': ride_execution.stopplanID,
            'trainID': ride_execution.trainID,
            'employees': employee_list
        })

    # Liste der Fahrten als JSON zurückgeben
    return jsonify(ride_executions_list)


@app.route('/ride_execution/<int:ride_execution_id>', methods=['DELETE'])
def delete_ride_execution(ride_execution_id):
    # Versuch, die Fahrt anhand der ID zu finden
    ride_execution = RideExecution.query.get_or_404(ride_execution_id)

    # Fahrt aus der Datenbank löschen
    db.session.delete(ride_execution)
    db.session.commit()

    # Bestätigung der Löschung zurückgeben
    return jsonify({'message': 'Ride_Execution deleted'}), 200


@app.route('/ride_execution/<int:ride_execution_id>', methods=['PUT'])
def update_ride_execution(ride_execution_id):
    # Versuch, die Fahrt anhand der ID zu finden
    ride_execution = RideExecution.query.get(ride_execution_id)

    # Falls die Fahrt nicht gefunden wurde, Fehler zurückgeben
    if not ride_execution:
        return jsonify({"error": "RideExecution not found"}), 404

    # Die zu aktualisierenden Daten aus der Anfrage holen
    data = request.get_json()

    # Überprüfen, ob 'isCanceled' in den Daten enthalten ist
    if 'isCanceled' in data:
        if data['isCanceled'] == "Ja":
            ride_execution.isCanceled = True
            ride_execution.delay = 0  # Falls die Fahrt abgesagt ist, Verzögerung auf 0 setzen
        else:
            ride_execution.isCanceled = False

    # Verzögerung aktualisieren, falls angegeben
    if 'delay' in data:
        ride_execution.delay = data['delay']

    try:
        # Änderungen in der Datenbank speichern
        db.session.commit()
        return jsonify({
            "message": "RideExecution updated successfully",
            "rideExecution": {
                'id': ride_execution.id,
                'price': ride_execution.price,
                'isCanceled': ride_execution.isCanceled,
                'delay': ride_execution.delay,
                'stopplanID': ride_execution.stopplanID,
                'trainID': ride_execution.trainID
            }
        }), 200
    except Exception as e:
        # Falls ein Fehler auftritt, Änderungen zurücksetzen und Fehlernachricht zurückgeben
        db.session.rollback()
        return jsonify({"error": f"Update failed: {str(e)}"}), 500


@app.route("/employees")
@cross_origin()
def get_all_employees():
    # Alle Mitarbeiter aus der Datenbank abrufen
    employees = Employee.query.all()
    employee_list = []

    # Liste der Mitarbeiter erstellen
    for employee in employees:
        rideExecution_list = []
        # Für jeden Mitarbeiter die Fahrten abrufen, an denen er beteiligt ist
        for ride_execution in employee.rideExecutions:
            rideExecution_list.append({
                'id': ride_execution.id,
                'price': ride_execution.price,
                'isCanceled': ride_execution.isCanceled,
                'delay': ride_execution.delay,
                'date': ride_execution.date.strftime('%d.%m.%Y'),  # Datum im Format dd.MM.yyyy
                'time': ride_execution.time.strftime('%H:%M'),  # Uhrzeit im Format HH:mm
                'stopplan': {
                    'name': ride_execution.stopplan.name,
                },
                'trainID': ride_execution.trainID
            })

        # Die Mitarbeiterdaten mit Fahrten zusammenstellen
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

    # Liste der Mitarbeiter als JSON zurückgeben
    return jsonify(employee_list)
