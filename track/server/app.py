from flask import Flask
from routes.EmployeeRoutes import employee_blueprint
from routes.TrainStationRoutes import trainstation_blueprint

app = Flask(__name__)

app.register_blueprint(employee_blueprint, url_prefix='/employees')
app.register_blueprint(trainstation_blueprint, url_prefix='/track/train-stations')

if __name__ == "__main__":
    app.run(debug=True)
