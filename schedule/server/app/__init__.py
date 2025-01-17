import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_migrate import Migrate

db = SQLAlchemy()
DB_NAME = "database.db"
DATABASE_URL = f"sqlite:///{os.path.abspath('server/db/database.db')}"


app = Flask(__name__)
app.config['SECRET_KEY'] = 'asdf'
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
db.init_app(app)
migrate = Migrate(app, db)

def create_database(app):
    if not path.exists('website/' + DB_NAME):
        with app.app_context():
            db.create_all()
            print('Created Database!')

from app import routes

from app import models


# Rufe die Funktion auf, um die Datenbank zu erstellen
create_database(app)
