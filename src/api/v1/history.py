from src.db.model import AccessHistory, UserRole, Role
from http import HTTPStatus

from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.db.db_config import Base, engine, db_session


history_bp = Blueprint('history', __name__)
Base.metadata.bind = engine


@history_bp.route('/', methods=['GET'])
@jwt_required()
def get_my_access_history():
    user_id = get_jwt_identity()
    u_r = db_session.query(UserRole).filter(UserRole.user_id == user_id).first()
    role = db_session.query(Role).filter(Role.id == u_r.role_id).first()
    if role.role_name != 'guest':
        access_history_records = db_session.query(AccessHistory).filter(
            AccessHistory.user_id == user_id
        ).all()
        serialized_access_history_records = [
            {
                'id': record.id,
                'user_id': record.user_id,
                'action': record.action,
                'created': record.created,
            }
            for record in access_history_records
        ]
        return jsonify(serialized_access_history_records), HTTPStatus.OK
    else:
        return jsonify({'message': 'Permission denied'}), HTTPStatus.FORBIDDEN


@history_bp.route('/all', methods=['GET'])
@jwt_required()
def get_all_access_history():
    user_id = get_jwt_identity()
    u_r = db_session.query(UserRole).filter(UserRole.user_id == user_id).first()
    role = db_session.query(Role).filter(Role.id == u_r.role_id).first()
    if role.role_name in ('superuser', 'admin'):
        access_history_records = db_session.query(AccessHistory).all()
        serialized_access_history_records = [
            {
                'id': record.id,
                'user_id': record.user_id,
                'action': record.action,
                'created': record.created,
            }
            for record in access_history_records
        ]
        return jsonify(serialized_access_history_records), HTTPStatus.OK
    else:
        return jsonify({'message': 'Permission denied'}), HTTPStatus.FORBIDDEN
