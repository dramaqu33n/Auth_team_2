from http import HTTPStatus

from flask import jsonify

from src.db.db_config import Base, engine, db_session
from src.db.model import AccessHistory, User


Base.metadata.bind = engine


def get_user_access_history(user_id, page, per_page):
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


def get_access_history(user_id, page, per_page):
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
