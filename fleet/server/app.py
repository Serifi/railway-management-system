from flask import Flask
from routes.EmployeeRoutes import employee_blueprint
from routes.CarriageRoutes import carriage_blueprint

app = Flask(__name__)

app.register_blueprint(employee_blueprint, url_prefix='/employees')
app.register_blueprint(carriage_blueprint, url_prefix='/fleet/carriages')

if __name__ == "__main__":
    app.run(debug=True)
