from http import HTTPStatus

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from jsonschema import validate

from src.schemas.auth_schemas import register_schema, login_schema
from src.schemas.auth_schemas import password_reset_schema
from src.services.auth_service import refresh_user_access_token, get_user_info
from src.services.auth_service import register_user, user_logout, user_login
from src.services.auth_service import reset_user_password


auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    try:
        validate(data, register_schema)
    except Exception as e:
        return jsonify(
            {'message': 'Invalid input parameters', 'error': str(e)},
        ), HTTPStatus.BAD_REQUEST
    return register_user(data)


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    try:
        validate(data, login_schema)
    except Exception as e:
        return jsonify(
            {'message': 'Invalid input parameters', 'error': str(e)},
        ), HTTPStatus.BAD_REQUEST
    user_agent = request.headers.get("User-Agent")
    return user_login(data, user_agent)


@auth_bp.route('/password-reset', methods=['POST'])
@jwt_required()
def password_reset():
    data = request.get_json()
    try:
        validate(data, password_reset_schema)
    except Exception as e:
        return jsonify(
            {'message': 'Invalid input parameters', 'error': str(e)},
        ), HTTPStatus.BAD_REQUEST
    user_id = get_jwt_identity()
    return reset_user_password(data, user_id)


@auth_bp.route('/refresh', methods=['GET'])
@jwt_required(refresh=True)
def refresh():
    user_id = get_jwt_identity()
    user_agent = request.headers.get('User-Agent')
    return refresh_user_access_token(user_id, user_agent)


@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    user_id = get_jwt_identity()
    user_agent = request.headers.get('User-Agent')
    return user_logout(user_id, user_agent)


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def my_info():
    user_id = get_jwt_identity()
    return get_user_info(user_id)
