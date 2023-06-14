import yaml

from flasgger import Swagger
from flask import Flask, Blueprint, request
from flask_jwt_extended import JWTManager
from flask_login import LoginManager

from src.api.v1.auth import auth_bp
from src.api.v1.health import health_bp
from src.api.v1.history import history_bp
from src.api.v1.oauth import oauth_bp, oauth
from src.api.v1.roles import roles_bp
from src.core.config import settings
from src.db.db_config import db_session
from src.db.model import User

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.resources import Resource       
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.exporter.jaeger.thrift import JaegerExporter


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

configure_tracer()


app = Flask(__name__)
FlaskInstrumentor().instrument_app(app) 

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
    return db_session.get(User, user_id)


@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    user_id = jwt_data["sub"]
    return db_session.get(User, user_id)


api_bp = Blueprint('api_v1', __name__, url_prefix='/api/v1')
api_bp.register_blueprint(auth_bp, url_prefix='/auth')
api_bp.register_blueprint(oauth_bp, url_prefix='/oauth')
api_bp.register_blueprint(roles_bp, url_prefix='/roles')
api_bp.register_blueprint(history_bp, url_prefix='/history')
api_bp.register_blueprint(health_bp, url_prefix='/health')

app.register_blueprint(api_bp)

app.secret_key = settings.secret_key
oauth.init_app(app)


if __name__ == '__main__':
    app.run()
