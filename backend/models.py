from config import db
from flask_login import UserMixin
from datetime import datetime, timezone

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    hashed_password = db.Column(db.String(300), nullable=False)

class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(40), nullable=False)
    description = db.Column(db.String(200))
    amount = db.Column(db.Float)
    date = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship("User", backref = db.backref("expenses"), lazy=True)