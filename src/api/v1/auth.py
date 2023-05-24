from flask import Blueprint, request, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required
from src.db.db_config import Base, engine, db_session
from src.db.model import User, AccessHistory
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from http import HTTPStatus

auth_bp = Blueprint('auth', __name__)

login_manager = LoginManager()
login_manager.login_view = 'auth.login'

Base.metadata.bind = engine


@login_manager.user_loader
def load_user(user_id):
    session = db_session()
    return session.query(User).get(user_id)


@auth_bp.route('/register', methods=['POST'])
def register():
    session = db_session()
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')
    role = data.get('role', 'user')
    existing_user = session.query(User).filter_by(username=username).first()
    if existing_user:
        return jsonify({'message': 'Username already exists'}), HTTPStatus.CONFLICT
    new_user = User(
        username=username,
        email=email,
        role=role,
        created=datetime.utcnow(),
        modified=datetime.utcnow()
    )
    new_user.set_password(password)
    session.add(new_user)
    session.commit()
    return jsonify({'message': 'User registered successfully'}), HTTPStatus.OK

@auth_bp.route('/login', methods=['POST'])
def login():
    session = db_session()
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    user = session.query(User).filter_by(username=username).first()
    if user and user.check_password(password):
        login_user(user)
        access_history = AccessHistory(
            user_id=user.id,
            action='login',
            created=datetime.utcnow()
        )
        session.add(access_history)
        session.commit()
        return jsonify({'message': 'Login successful'}), HTTPStatus.OK
    return jsonify({'message': 'Invalid username or password'}), HTTPStatus.UNAUTHORIZED


@auth_bp.route('/password-reset', methods=['POST'])
@login_required
def password_reset():
    session = db_session()
    current_user = load_user()
    data = request.get_json()
    new_password = data.get('new_password')
    current_user.set_password(new_password)
    current_user.modified = datetime.utcnow()
    session.commit()
    return jsonify({'message': 'Password reset successfully'})


@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({'message': 'Logout successful'})
