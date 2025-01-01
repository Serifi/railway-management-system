from flask import Flask
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint
from swagger_docs import swagger_template
from flask import jsonify
from routes.employee_routes import employee_blueprint
from routes.carriage_routes import carriage_blueprint
from routes.train_routes import train_blueprint
from routes.maintenance_routes import maintenance_blueprint

app = Flask(__name__)
app.url_map.strict_slashes = False

swaggerui_blueprint = get_swaggerui_blueprint(
    '/docs',
    '/docs/swagger.json',
    config={'app_name': "Fleet"}
)

app.register_blueprint(employee_blueprint, url_prefix='/employees')
app.register_blueprint(carriage_blueprint, url_prefix='/fleet/carriages')
app.register_blueprint(train_blueprint, url_prefix='/fleet/trains')
app.register_blueprint(maintenance_blueprint, url_prefix='/fleet/maintenances')
app.register_blueprint(swaggerui_blueprint, url_prefix='/docs')

CORS(app)

@app.after_request
def add_cors_headers(response):
    response.headers.add('Access-Control-Allow-Origin', 'http://localhost:3000')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
    return response

@app.route('/docs/swagger.json')
def swagger_json():
    return jsonify(swagger_template)

if __name__ == "__main__":
    app.run(debug=True)