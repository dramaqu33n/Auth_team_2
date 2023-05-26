from datetime import datetime
from datetime import timedelta
from http import HTTPStatus

from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_login import LoginManager, login_user, logout_user, login_required, current_user

from src.db.db_config import Base, engine, db_session
from src.db.model import User, AccessHistory
from src.db.redis import TokenStorage


auth_bp = Blueprint('auth', __name__)


Base.metadata.bind = engine
token_storage = TokenStorage()


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password') or ''
    email = data.get('email')
    role = data.get('role', 'user')
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return jsonify(
            {'message': 'Username already exists'},
        ), HTTPStatus.CONFLICT
    new_user = User(
        username=username,
        email=email,
        role=role,
    )
    new_user.set_password(password)
    db_session.add(new_user)
    db_session.commit()
    return jsonify({'message': 'User registered successfully'}), HTTPStatus.OK

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        login_user(user)
        access_history = AccessHistory(
            user_id=user.id,
            action='login',
            created=datetime.utcnow()
        )
        db_session.add(access_history)
        db_session.commit()
        access_token = create_access_token(
            identity=str(user.id),
            expires_delta=timedelta(minutes=15),
        )
        refresh_token = create_refresh_token(
            identity=str(user.id),
            expires_delta=timedelta(days=30),
        )
        user_agent = request.headers.get("User-Agent")
        token_storage.store_token(
            "access",
            str(user.id),
            user_agent,
            access_token,
        )
        token_storage.store_token(
            "refresh",
            str(user.id),
            user_agent,
            refresh_token,
        )
        return jsonify(
            access_token=access_token,
            refresh_token=refresh_token,
        ), HTTPStatus.OK
    return jsonify({'message': 'Invalid username or password'}), HTTPStatus.UNAUTHORIZED


@auth_bp.route('/password-reset', methods=['POST'])
@jwt_required()
def password_reset():
    data = request.get_json()
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if user:
        new_password = data.get('new_password') or ''
        user.set_password(new_password)
        user.modified = datetime.utcnow()
        db_session.commit()
        return jsonify({'message': 'Password reset successfully'})
    else:
        return jsonify({'message': 'User not found'}), HTTPStatus.NOT_FOUND


@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    logout_user()
    return jsonify({'message': 'Logout successful'})
