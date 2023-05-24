from flask import Blueprint, request, jsonify
from db.model import Right, Role
from db.db_config import Base, engine, db_session


rights_bp = Blueprint('rights', __name__)
Base.metadata.bind = engine


@rights_bp.route('/', methods=['GET'])
def list_rights():
    session = db_session()
    rights = session.query(Right).all()
    serialized_rights = [
        {
            'id': right.id,
            'name': right.right_name,
            'created': right.created,
            'modified': right.modified
        }
        for right in rights
    ]
    return jsonify(serialized_rights)


@rights_bp.route('/rights', methods=['POST'])
def create_right():
    session = db_session()
    data = request.get_json()
    name = data.get('name')
    new_right = Right(right_name=name)
    session.add(new_right)
    session.commit()
    return jsonify({'message': 'Right created successfully'}), 201


@rights_bp.route('/rights/<right_id>', methods=['GET'])
def get_right(right_id):
    session = db_session()
    right = session.query(Right).get(right_id)
    if right:
        serialized_right = {
            'id': right.id,
            'name': right.right_name,
            'created': right.created,
            'modified': right.modified
        }
        return jsonify(serialized_right)
    return jsonify({'message': 'Right not found'}), 404


@rights_bp.route('/rights/<right_id>', methods=['PUT'])
def update_right(right_id):
    session = db_session()
    right = session.query(Right).get(right_id)
    if right:
        data = request.get_json()
        name = data.get('name')
        right.right_name = name
        right.modified = datetime.utcnow()
        session.commit()
        return jsonify({'message': 'Right updated successfully'})
    return jsonify({'message': 'Right not found'}), 404


@rights_bp.route('/rights/<right_id>', methods=['DELETE'])
def delete_right(right_id):
    session = db_session()
    right = session.query(Right).get(right_id)
    if right:
        session.delete(right)
        session.commit()
        return jsonify({'message': 'Right deleted successfully'})
    return jsonify({'message': 'Right not found'}), 404


@rights_bp.route('/roles/<role_id>/rights', methods=['GET'])
def get_role_rights(role_id):
    session = db_session()
    role = session.query(Role).get(role_id)
    if role:
        serialized_rights = [
            {
                'id': right.id,
                'name': right.right_name,
                'created': right.created,
                'modified': right.modified
            }
            for right in role.rights
        ]
        return jsonify(serialized_rights)
    return jsonify({'message': 'Role not found'}), 404


@rights_bp.route('/roles/<role_id>/rights', methods=['PUT'])
def update_role_rights(role_id):
    session = db_session()
    role = session.query(Role).get(role_id)
    if role:
        data = request.get_json()
        rights = data.get('rights')
        if isinstance(rights, list):
            rights = session.query(Right).filter(Right.id.in_(rights)).all()
            role.rights.clear()
            role.rights.extend(rights)
            session.commit()
            return jsonify({'message': 'Rights updated successfully'})
    return jsonify({'message': 'Role not found or invalid data'}), 404


