from flask import Flask
from routes.EmployeeRoutes import employee_blueprint
from routes.CarriageRoutes import carriage_blueprint
from flask_cors import CORS

app = Flask(__name__)
app.url_map.strict_slashes = False
app.register_blueprint(employee_blueprint, url_prefix='/employees')
app.register_blueprint(carriage_blueprint, url_prefix='/fleet/carriages')
CORS(app)

@app.after_request
def add_cors_headers(response):
    response.headers.add('Access-Control-Allow-Origin', 'http://localhost:3000')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
    return response

if __name__ == "__main__":
    app.run(debug=True)