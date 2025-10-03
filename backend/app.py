from config import app, db, login_manager
from models import User, Expense
from flask import request
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from markupsafe import escape
from json import jsonify


@login_manager.user_loader
def load_user(id):
    return User.query.get(id)


@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        data = request.get_json()
        anon_user_email = data.get("email")
        anon_user_password = data.get("password")
        user = User.query.filter_by(email=anon_user_email).first()
        if user and check_password_hash(user.password, anon_user_password):
            login_user(user)
            return jsonify({"message": "the user has been logged in."}), 200
        return jsonify({"message": "the user email is not found in the database"}), 400


@app.route("/logout", methods=["POST", "GET"])
@login_required
def logout():
    if request.method == "POST":
        logout_user()
        return jsonify({"message": "user has been logged out"}), 200


@app.route("/sign_up", methods=["POST", "GET"])
def sign_up():
    if request.method == "POST":
        data: dict = request.get_json()
        if data is None:
            return jsonify({"error": "Invalid JSON format or missing data"}), 400

        if "email" not in data or "password" not in data:
            return jsonify({"error": "Missing required fields (email, password)"}), 400

        user_email = data.get("email")
        user_password = data.get("password")
        checking_user_email = User.query.filter_by(email=user_email).first()

        if checking_user_email:
            return jsonify({"message": "This email is already in use."}), 400

        hashed_password = generate_password_hash(
            user_password, method="pbkdf2:sha1", salt_length=24
        )

        new_user = User(email=user_email, hashed_password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return (
            jsonify({"message": "User successfully registered!"}),
            201,
        )  # HTTP Status 201 (Created)


@app.route("/sign_out", methods=["POST", "GET"])
@login_required
def sign_out():
    if request.method == "POST":
        db.session.delete(current_user)
        db.session.commit()
        logout_user()
        return jsonify({"message": "this user has been deleted and logged out"}), 200


def create():
    if request.method == "POST":
        data: dict = request.get_json()
        category = data.get("category")
        description = data.get("description")
        amount = data.get("amount")

        expense = Expense(category=category, description=description, amount=amount)
        db.session.add(expense)
        db.session.commit()


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=8000)
