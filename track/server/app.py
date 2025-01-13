# Hauptanwendung für das Backend
from flask import Flask
from routes.EmployeeRoutes import employee_blueprint
from routes.TrainStationRoutes import trainstation_blueprint
from routes.WarningRoutes import warning_blueprint
from routes.SectionRoutes import section_blueprint
from routes.TrackRoutes import track_blueprint
from flask_cors import CORS

# Flask-App erstellen
app = Flask(__name__)

# Entfernt das strikte Anhängen von Slashes in URL
app.url_map.strict_slashes = False

# Registrierung der Blueprints für verschiedenen Routen
app.register_blueprint(employee_blueprint, url_prefix='/employees')  # Endpunkte für Mitarbeiter
app.register_blueprint(trainstation_blueprint, url_prefix='/track/train-stations')  # Endpunkte für Bahnhöfe
app.register_blueprint(warning_blueprint, url_prefix='/track/warnings')  # Endpunkte für Warnungen
app.register_blueprint(section_blueprint, url_prefix='/track/sections')  # Endpunkte für Abschnitte
app.register_blueprint(track_blueprint, url_prefix='/track/tracks')  # Endpunkte für Strecken

# Aktivieren von CORS für App
CORS(app)

# CORS-Header zu allen Antworten hinzufügen
@app.after_request
def add_cors_headers(response):
    response.headers.add('Access-Control-Allow-Origin', 'http://localhost:3000')  # Erlauben der Anfragen von localhost:3000
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')  # Erlauben von HTTP-Methoden
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization') # Erlauben verschiedener Header
    return response

# Starten der App
if __name__ == "__main__":
    app.run(debug=True)