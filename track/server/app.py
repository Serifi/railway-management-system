from flask import Flask
from flask_restx import Api
from routes.TrainStationRoutes import trainstation_namespace
#from routes.EmployeeRoutes import employee_blueprint
#from routes.TrainStationRoutes import trainstation_blueprint

app = Flask(__name__)

#app.register_blueprint(employee_blueprint, url_prefix='/employees')
#app.register_blueprint(trainstation_blueprint, url_prefix='/track/train-stations')

api = Api(app, version='1.0', title='Track', description='API for managing tracks')
api.add_namespace(trainstation_namespace, path='/track/train-stations')

if __name__ == "__main__":
    app.run(debug=True)
