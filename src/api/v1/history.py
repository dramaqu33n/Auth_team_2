from src.db.model import AccessHistory, User
from http import HTTPStatus

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.db.db_config import Base, engine, db_session


history_bp = Blueprint('history', __name__)
Base.metadata.bind = engine


@history_bp.route('/', methods=['GET'])
@jwt_required()
def get_my_access_history():
    page = request.args.get('page', default=1, type=int)
    per_page = request.args.get('per_page', default=10, type=int)
    user_id = get_jwt_identity()
    user = db_session.query(User).filter(User.id == user_id).first()
    roles = [role.role_name for role in user.roles]
    if roles[0] != 'guest':
        access_history_records = db_session.query(AccessHistory).filter(
            AccessHistory.user_id == user_id
        )
        paginated_access_history = access_history_records.limit(per_page).offset(
            (page - 1) * per_page
        ).all()
        serialized_access_history_records = [
            {
                'id': record.id,
                'user_id': record.user_id,
                'action': record.action,
                'created': record.created,
            }
            for record in paginated_access_history
        ]
        return jsonify(serialized_access_history_records), HTTPStatus.OK
    else:
        return jsonify({'message': 'Permission denied'}), HTTPStatus.FORBIDDEN


@history_bp.route('/all', methods=['GET'])
@jwt_required()
def get_all_access_history():
    page = request.args.get('page', default=1, type=int)
    per_page = request.args.get('per_page', default=10, type=int)
    user_id = get_jwt_identity()
    user = db_session.query(User).filter(User.id == user_id).first()
    roles = [role.role_name for role in user.roles]
    if not set(roles) & set(('superuser', 'admin')):
        return jsonify({'message': 'Permission denied'}), HTTPStatus.FORBIDDEN
    access_history_records = db_session.query(AccessHistory)
    paginated_access_history = access_history_records.limit(per_page).offset(
        (page - 1) * per_page
    ).all()
    serialized_access_history_records = [
        {
            'id': record.id,
            'user_id': record.user_id,
            'action': record.action,
            'created': record.created,
        }
        for record in paginated_access_history
    ]
    return jsonify(serialized_access_history_records), HTTPStatus.OK
