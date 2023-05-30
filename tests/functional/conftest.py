from src.app import app
from src.db.db_config import db_session

from src.db.model import User
from src.logs.log_config import logger
from http import HTTPStatus
from time import sleep
import pytest
from flask import json
from src.core.config import settings

@pytest.fixture
def authenticated_client():
    tester = app.test_client()
    new_user = {
        'username': 'ivan.ivanov',
        'password': 'ivanov666',
        'email': 'ivan@ivanov.com',
    }
    response = tester.post(
        'api/v1/auth/register',
        data=json.dumps(new_user),
        content_type='application/json',
    )
    response = tester.post(
        'api/v1/auth/login',
        data=json.dumps({
            'username': 'ivan.ivanov',
            'password': 'ivanov666',
        }),
        content_type='application/json',
    )
    response_data = json.loads(response.data)
    access_token = response_data['access_token']
    tester.access_token = access_token
    return tester


@pytest.fixture
def authenticated_superuser():
    tester = app.test_client()
    response = tester.post(
        'api/v1/auth/login',
        data=json.dumps({
            'username': settings.superuser_name,
            'password': settings.superuser_pass,
        }),
        content_type='application/json',
    )
    response_data = json.loads(response.data)
    access_token = response_data['access_token']
    tester.access_token = access_token
    return tester

@pytest.fixture(autouse=True)
def cleanup():
    yield
    with app.app_context():
        test_user = db_session.query(User).filter_by(username='ivan.ivanov').first()
        if test_user:
            db_session.delete(test_user)
            db_session.commit()
            logger.info('Deleted user %s', test_user)
