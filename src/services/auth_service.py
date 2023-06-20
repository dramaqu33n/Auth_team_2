from datetime import datetime, timedelta
from http import HTTPStatus

from flask import jsonify
from flask_jwt_extended import create_access_token, create_refresh_token
from flask_login import login_user, logout_user

from src.db.db_config import db
from src.db.model import User, AccessHistory, Role
from src.db.redis import TokenStorage, TokenType


token_storage = TokenStorage()
db_session = db.session


def register_user(data):
    username = data.get('username')
    password = data.get('password', '')
    email = data.get('email')
    name = data.get('name', '')
    surname = data.get('surname', '')
    role = data.get('role', 'user')
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return jsonify(
            {'message': 'Username already exists'},
        ), HTTPStatus.CONFLICT
    user_role = Role.query.filter_by(role_name=role).first()
    new_user = User(
        username=username,
        email=email,
        name=name,
        surname=surname,
    )
    new_user.set_password(password)
    new_user.roles.append(user_role)
    db_session.add(new_user)
    db_session.commit()
    return jsonify({'message': 'User registered successfully'}), HTTPStatus.OK


def user_login(data, user_agent):
    username = data.get('username')
    password = data.get('password')
    user = User.query.filter_by(username=username).first()
    if not user or not user.check_password(password):
        return jsonify(
            {'message': 'Invalid username or password'},
        ), HTTPStatus.UNAUTHORIZED
    login_user(user)
    access_history = AccessHistory(
        user_id=user.id,
        action='login',
        created=datetime.utcnow(),
        user_agent=user_agent,

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
    token_storage.store_token(
        TokenType.ACCESS,
        str(user.id),
        user_agent,
        access_token,
    )
    token_storage.store_token(
        TokenType.REFRESH,
        str(user.id),
        user_agent,
        refresh_token,
    )
    return jsonify(
        access_token=access_token,
        refresh_token=refresh_token,
    ), HTTPStatus.OK


def reset_user_password(data, user_id):
    user = db_session.get(User, user_id)
    if user:
        new_password = data.get('new_password') or ''
        user.set_password(new_password)
        user.modified = datetime.utcnow()
        db_session.commit()
        return jsonify({'message': 'Password reset successfully'}), HTTPStatus.OK
    else:
        return jsonify({'message': 'User not found'}), HTTPStatus.NOT_FOUND


def refresh_user_access_token(user_id, user_agent):
    token_storage.invalidate_token(
        TokenType.ACCESS,
        user_id,
        user_agent,
    )
    new_token = create_access_token(identity=user_id)
    token_storage.store_token(
        TokenType.ACCESS,
        user_id,
        user_agent,
        new_token,
    )
    return jsonify({'access_token': new_token}), HTTPStatus.OK


def user_logout(user_id, user_agent):
    logout_user()
    token_storage.invalidate_token(TokenType.ACCESS, user_id, user_agent)
    return jsonify(
        {'message': 'Logout successful, access_token revoked'},
    ), HTTPStatus.OK


def get_user_info(user_id):
    me = db_session.get(User, user_id)
    my_info = {
        'username': me.username,
        'name': me.name,
        'surname': me.surname,
        'email': me.email,
        'account created': me.created,
        'user_id': me.id
    }
    return jsonify(my_info), HTTPStatus.OK
