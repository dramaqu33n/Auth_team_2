from http import HTTPStatus


health_bp = Blueprint('health', __name__)


@health_bp.route('/', methods=['GET'])
def get_heartbeat():
    return jsonify({}), HTTPStatus.OK
