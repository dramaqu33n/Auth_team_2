from flask import Blueprint, request, jsonify
from src.db.model import Role
from src.db.db_config import Base, engine, db_session
from datetime import datetime

roles_bp = Blueprint('roles', __name__)
Base.metadata.bind = engine


@roles_bp.route('/', methods=['GET'])
def list_roles():
    session = db_session()
    roles = session.query(Role).all()
    serialized_roles = [
        {
            'id': role.id,
            'name': role.role_name,
            'created': role.created,
            'modified': role.modified
        }
        for role in roles
    ]
    return jsonify(serialized_roles)


@roles_bp.route('/', methods=['POST'])
def create_role():
    session = db_session()
    data = request.get_json()
    name = data.get('name')
    new_role = Role(role_name=name)
    session.add(new_role)
    session.commit()
    return jsonify({'message': 'Role created successfully'}), 201


@roles_bp.route('/<role_id>', methods=['GET'])
def get_role(role_id):
    session = db_session()
    role = session.query(Role).get(role_id)
    if role:
        serialized_role = {
            'id': role.id,
            'name': role.role_name,
            'created': role.created,
            'modified': role.modified
        }

        return jsonify(serialized_role)
    return jsonify({'message': 'Role not found'}), 404


@roles_bp.route('/<role_id>', methods=['PUT'])
def update_role(role_id):
    session = db_session()
    role = session.query(Role).get(role_id)
    if role:
        data = request.get_json()
        name = data.get('name')
        role.role_name = name
        role.modified = datetime.utcnow()
        session.commit()
        return jsonify({'message': 'Role updated successfully'})
    return jsonify({'message': 'Role not found'}), 404


@roles_bp.route('/<role_id>', methods=['DELETE'])
def delete_role(role_id):
    session = db_session()
    role = session.query(Role).get(role_id)
    if role:
        session.delete(role)
        session.commit()
        return jsonify({'message': 'Role deleted successfully'})
    return jsonify({'message': 'Role not found'}), 404
