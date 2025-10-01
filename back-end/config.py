from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
import os


backend_path = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__) #, instance_path=os.path.join(backend_path, "../databse/instance")

app.secret_key = "whatinthehellamisupposedtowritehere?generateanultrastrongpassword?"

login_manager = LoginManager()
login_manager.init_app(app)

app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:patate@localhost:5433/test"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)