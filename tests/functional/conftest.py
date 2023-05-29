from src.app import app
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
