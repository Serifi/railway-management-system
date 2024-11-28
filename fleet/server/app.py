from flask import Flask
from routes.EmployeeRoutes import employee_blueprint

app = Flask(__name__)

app.register_blueprint(employee_blueprint, url_prefix='/employees')

if __name__ == "__main__":
    app.run(debug=True)
