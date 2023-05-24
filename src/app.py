from flask import Flask
from flask_login import LoginManager

from api.v1.auth import auth_bp
from api.v1.roles import roles_bp
from api.v1.rights import rights_bp


app = Flask(__name__)
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(roles_bp, url_prefix='/roles')
app.register_blueprint(rights_bp, url_prefix='/rights')


if __name__ == '__main__':
    app.run()
