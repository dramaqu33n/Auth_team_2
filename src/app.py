from flask import Flask, Blueprint
from flask_login import LoginManager

from src.api.v1.auth import auth_bp
from src.api.v1.roles import roles_bp
from src.api.v1.rights import rights_bp
from src.core.config import settings


app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)

api_bp = Blueprint('api_v1', __name__, url_prefix='/api/v1')

api_bp.register_blueprint(auth_bp, url_prefix='/auth')
api_bp.register_blueprint(roles_bp, url_prefix='/roles')
api_bp.register_blueprint(rights_bp, url_prefix='/rights')

app.register_blueprint(api_bp)

app.secret_key = settings.secret_key

if __name__ == '__main__':
    app.run()
