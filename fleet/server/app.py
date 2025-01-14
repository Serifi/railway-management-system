from flask import Flask, jsonify
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint
from swagger_docs import swagger_template
from routes.employee_routes import employee_blueprint
from routes.carriage_routes import carriage_blueprint
from routes.train_routes import train_blueprint
from routes.maintenance_routes import maintenance_blueprint

app = Flask(__name__)
app.url_map.strict_slashes = False # Routes without trailing slashes

# Register blueprints for route handling & Swagger for API documentation
app.register_blueprint(employee_blueprint, url_prefix='/employees')
app.register_blueprint(carriage_blueprint, url_prefix='/fleet/carriages')
app.register_blueprint(train_blueprint, url_prefix='/fleet/trains')
app.register_blueprint(maintenance_blueprint, url_prefix='/fleet/maintenances')
app.register_blueprint(get_swaggerui_blueprint('/fleet/docs','/fleet/docs/swagger.json'), url_prefix='/fleet/docs')

CORS(app)
@app.after_request
def add_cors_headers(response):
    """ CORS headers in the response to allow communication with the frontend """
    response.headers.add('Access-Control-Allow-Origin', 'http://localhost:3000')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
    return response

@app.route('/fleet/docs/swagger.json')
def swagger_json():
    """ Endpoint to serve the API documentation """
    return jsonify(swagger_template)

if __name__ == "__main__":
    app.run(debug=True)