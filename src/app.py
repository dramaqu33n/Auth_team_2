from flask import Flask, Blueprint
from flask_jwt_extended import JWTManager
from flask_login import LoginManager
from flasgger import Swagger
import yaml

from src.api.v1.auth import auth_bp
from src.api.v1.history import history_bp
from src.api.v1.roles import roles_bp
from src.core.config import settings
from src.db.db_config import db_session
from src.db.model import User


app = Flask(__name__)

with open('src/apidocs.yaml', 'r') as stream:
    template = yaml.safe_load(stream)

swagger_config = {
    "headers": [
    ],
    "specs": [
        {
            "endpoint": '/api/v1',
            "route": '/api/v1',
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    # "static_folder": "static",  # must be set by user
    "swagger_ui": True,
    "specs_route": "/apidocs/"
}
swagger = Swagger(app, template=template, config=swagger_config)

jwt = JWTManager(app)
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def user_loader(user_id):
    return db_session.get(User, user_id)


api_bp = Blueprint('api_v1', __name__, url_prefix='/api/v1')
api_bp.register_blueprint(auth_bp, url_prefix='/auth')
api_bp.register_blueprint(roles_bp, url_prefix='/roles')
api_bp.register_blueprint(history_bp, url_prefix='/history')

app.register_blueprint(api_bp)

app.secret_key = settings.secret_key

if __name__ == '__main__':
    app.run()
