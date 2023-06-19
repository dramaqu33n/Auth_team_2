from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from src.services.history_service import get_access_history
from src.services.history_service import get_user_access_history


history_bp = Blueprint('history', __name__)


@history_bp.route('/', methods=['GET'])
@jwt_required()
def get_my_access_history():
    page = request.args.get('page', default=1, type=int)
    per_page = request.args.get('per_page', default=10, type=int)
    user_id = get_jwt_identity()
    return get_user_access_history(user_id, page, per_page)


@history_bp.route('/all', methods=['GET'])
@jwt_required()
def get_all_access_history():
    page = request.args.get('page', default=1, type=int)
    per_page = request.args.get('per_page', default=10, type=int)
    user_id = get_jwt_identity()
    return get_access_history(user_id, page, per_page)
