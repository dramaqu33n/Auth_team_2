from flask import Blueprint, request
from flask_jwt_extended import jwt_required

from src.services.roles_service import delete_exact_role
from src.services.roles_service import get_all_roles, create_exact_role
from src.services.roles_service import get_exact_role, update_exact_role


roles_bp = Blueprint('roles', __name__)


@roles_bp.route('/', methods=['GET'])
@jwt_required()
def list_roles():
    return get_all_roles()

@roles_bp.route('/', methods=['POST'])
@jwt_required()
def create_role():
    data = request.get_json()
    return create_exact_role(data)


@roles_bp.route('/<role_id>', methods=['GET'])
@jwt_required()
def get_role(role_id):
    return get_exact_role(role_id)


@roles_bp.route('/<role_id>', methods=['PUT'])
@jwt_required()
def update_role(role_id):
    data = request.get_json()
    return update_exact_role(role_id, data)


@roles_bp.route('/<role_id>', methods=['DELETE'])
@jwt_required()
def delete_role(role_id):
    return delete_exact_role(role_id)
