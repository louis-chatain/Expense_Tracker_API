from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os


backend_path = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, instance_path=os.path.join(backend_path, "../databse/instance"))

app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:patate@localhost:5433/expense"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)