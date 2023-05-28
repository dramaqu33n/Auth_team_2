from datetime import datetime

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

from src.db.db_config import Base, engine, db_session
from src.db.model import Role


roles_bp = Blueprint('roles', __name__)
Base.metadata.bind = engine


@roles_bp.route('/', methods=['GET'])
@jwt_required()
def list_roles():
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
    return jsonify(serialized_roles), 200


@roles_bp.route('/', methods=['POST'])
@jwt_required()
def create_role():
    data = request.get_json()
    name = data.get('name')
    new_role = Role(role_name=name)
    db_session.add(new_role)
    db_session.commit()
    return jsonify({'message': 'Role created successfully'}), 201


@roles_bp.route('/<role_id>', methods=['GET'])
@jwt_required()
def get_role(role_id):
    role = db_session.get(Role, role_id)
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
@jwt_required()
def update_role(role_id):
    role = db_session.get(Role, role_id)
    if role:
        data = request.get_json()
        name = data.get('name')
        role.role_name = name
        role.modified = datetime.utcnow()
        db_session.commit()
        return jsonify({'message': 'Role updated successfully'})
    return jsonify({'message': 'Role not found'}), 404


@roles_bp.route('/<role_id>', methods=['DELETE'])
@jwt_required()
def delete_role(role_id):
    role = db_session.get(Role, role_id)
    if role:
        db_session.delete(role)
        db_session.commit()
        return jsonify({'message': 'Role deleted successfully'})
    return jsonify({'message': 'Role not found'}), 404
