import click
import yaml

from flasgger import Swagger
from flask import Flask, Blueprint, request, jsonify
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_login import LoginManager
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter

from src.api.v1.auth import auth_bp
from src.api.v1.health import health_bp
from src.api.v1.history import history_bp
from src.api.v1.oauth import oauth_bp, oauth
from src.api.v1.roles import roles_bp
from src.core.config import settings
from src.db.db_config import db
from src.db.model import User
from src.db.model import User, Role, UserRole
from src.logs.log_config import logger


DB_URI = f'postgresql://{settings.db_user}:{settings.db_password}@{settings.db_host}:{settings.db_port}/{settings.db_name}'


def configure_tracer() -> None:
    resource = Resource(attributes={
        "service.name": "auth_service"
    })
    trace.set_tracer_provider(TracerProvider(resource=resource))
    trace.get_tracer_provider().add_span_processor(
        BatchSpanProcessor(
            JaegerExporter(
                agent_host_name=settings.jaeger_host,
                agent_port=settings.jaeger_port,
            )
        )
    )
    trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))


def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = DB_URI
    db.init_app(app)
    if settings.enable_tracer.lower() in ['true', '1', 'yes']:
        configure_tracer()
        FlaskInstrumentor().instrument_app(app)
    if settings.enable_limiter.lower() in ['true', '1', 'yes']:
        Limiter(
            get_remote_address,
            app=app,
            default_limits=["200 per day", "100 per hour"],
            storage_uri=f"redis://{settings.redis_host}:{settings.redis_port}",
        )
    return app


app = create_app()


@app.before_request
def before_request():
    request_id = request.headers.get('X-Request-Id')
    tracer = trace.get_tracer(__name__)
    span = tracer.start_span('HTTP Request ID')
    span.set_attribute('http.request_id', request_id)
    span.end()
    if not request_id:
        raise RuntimeError('request id is required')


with open('src/apidocs.yaml', 'r') as stream:
    template = yaml.safe_load(stream)


swagger_config = Swagger.DEFAULT_CONFIG
swagger_config['title'] = 'Authorization Service API'
swagger_config['specs'][0]['endpoint'] = '/api/v1'
swagger_config['specs'][0]['route'] = '/api/v1'

swagger = Swagger(app, template=template, config=swagger_config)

jwt = JWTManager(app)
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def user_loader(user_id):
    return db.session.get(User, user_id)


@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    user_id = jwt_data["sub"]
    return db.session.get(User, user_id)


api_bp = Blueprint('api_v1', __name__, url_prefix='/api/v1')
api_bp.register_blueprint(auth_bp, url_prefix='/auth')
api_bp.register_blueprint(oauth_bp, url_prefix='/oauth')
api_bp.register_blueprint(roles_bp, url_prefix='/roles')
api_bp.register_blueprint(history_bp, url_prefix='/history')
api_bp.register_blueprint(health_bp, url_prefix='/health')

app.register_blueprint(api_bp)

app.secret_key = settings.secret_key

oauth.init_app(app)


@app.errorhandler(500)
def internal_server_error_handler(e):
    original_error = str(e.original_exception) if e.original_exception else ""
    response = {
        "error": "Что-то пошло не так",
        "description": "Мы работаем, чтобы это исправить",
        # "original error": original_error
    }
    return jsonify(response), 500


@app.cli.command("create_superuser")
def create_superuser() -> bool:
    '''There must be at least one superuser in our initial db'''
    superusername = click.prompt('Enter Username')
    name = click.prompt('Enter Name')
    surname = click.prompt('Enter Surname')
    email = click.prompt('Enter Email')
    password = click.prompt('Enter Password', hide_input=True)
    superuser_role = db.session.query(Role).filter_by(role_name='superuser').first()
    if not superuser_role:
        logger.critical('Create superuser role first in Role model')
        raise ValueError
    superuser_role_id = superuser_role.id

    superuser = User(
        username=superusername,
        name=name,
        surname=surname,
        email=email
    )

    superuser.set_password(password)
    logger.info('Superuser %s created', superuser)
    db.session.add(superuser)
    db.session.commit()
    superuser_role = UserRole(
        user_id=superuser.id,
        role_id=superuser_role_id
        )
    db.session.add(superuser_role)
    db.session.commit()
    return True


@app.cli.command('create_basic_roles')
def create_basic_roles(basic_roles: list[str] = ['superuser', 'admin', 'user', 'guest']):
    '''Creating basic role types in initial db'''
    for role_name in basic_roles:
        role = db.session.query(Role).filter_by(role_name=role_name).first()
        if role:
            logger.info('Role %s exists', role_name)
            continue
        role = Role(role_name=role_name)
        db.session.add(role)
        db.session.commit()
        logger.info('Role %s created', role_name)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run()
