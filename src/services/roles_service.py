from datetime import datetime
from http import HTTPStatus

from flask import jsonify

from src.db.db_config import db
from src.db.model import Role


db_session = db.session


def get_all_roles():
    roles = db_session.query(Role).all()
    serialized_roles = [
        {
            'id': role.id,
            'name': role.role_name,
            'created': role.created,
            'modified': role.modified
        }
        for role in roles
    ]
    return jsonify(serialized_roles), HTTPStatus.OK


def create_exact_role(data):
    name = data.get('name')
    new_role = Role(role_name=name)
    db_session.add(new_role)
    db_session.commit()
    return jsonify({'message': 'Role created successfully'}), HTTPStatus.CREATED


def get_exact_role(role_id):
    role = db_session.get(Role, role_id)
    if role:
        serialized_role = {
            'id': role.id,
            'name': role.role_name,
            'created': role.created,
            'modified': role.modified
        }

        return jsonify(serialized_role), HTTPStatus.OK
    return jsonify({'message': 'Role not found'}), HTTPStatus.NOT_FOUND


def update_exact_role(role_id, data):
    role = db_session.get(Role, role_id)
    if role:
        name = data.get('name')
        role.role_name = name
        role.modified = datetime.utcnow()
        db_session.commit()
        return jsonify({'message': 'Role updated successfully'})
    return jsonify({'message': 'Role not found'}), HTTPStatus.NOT_FOUND


def delete_exact_role(role_id):
    role = db_session.get(Role, role_id)
    if role:
        db_session.delete(role)
        db_session.commit()
        return jsonify({'message': 'Role deleted successfully'})
    return jsonify({'message': 'Role not found'}), HTTPStatus.NOT_FOUND
