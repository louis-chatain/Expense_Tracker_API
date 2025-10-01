from config import app, db, login_manager
from models import User, Expense
from flask import request
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from markupsafe import escape

@login_manager.user_loader
def load_user(id):
    return User.query.get(id)

def sign_up():
    data = request.get_json()
    user_email = data.get("email")
    user_password = data.get("password")
    checking_user_email = User.query.filter_by(email=user_email).first()

    if checking_user_email:
        return {"message": "This email is already i use."}
    
    hashed_password = generate_password_hash(user_password, method="pbkdf2:sha1", salt_length=24)

    new_user = User(email = user_email, hashed_password = hashed_password)
    db.session.add(new_user)
    db.session.commit()


def sign_out():
    db.session.delete(current_user)
    db.session.commit()
    logout_user()
    return {"message": "this user has been deleted and logged outs"}


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=8000)