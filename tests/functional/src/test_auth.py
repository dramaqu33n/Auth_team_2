from http import HTTPStatus
import jwt
import pytest
import random
import time

from flask import json

from src.app import app
from src.core.config import settings
from src.db.db_config import db_session
from src.db.model import User
from src.db.redis import TokenStorage
from src.logs.log_config import logger


@pytest.mark.parametrize(
    'data, expected_answer',
    [
        (
            {
                'username': 'test_user',
                'password': 'test_password',
                'email': 'test@email.com',
                'name': 'Testen',
                'surname': 'Testenson',
                'role': 'user',
            },
            {
                'status': HTTPStatus.OK,
                'message': 'User registered successfully'
            },
        ),
        (
            {
                'username': 'super.arnold',
                'password': 'test_password',
                'email': 'arnold@email.com',
            },
            {
                'status': HTTPStatus.CONFLICT,
                'message': 'Username already exists'
            },
        ),
    ],
)
def test_registration(data, expected_answer):
    tester = app.test_client()
    logger.info('DATA: %s', data)
    response = tester.post(
        'api/v1/auth/register',
        data=json.dumps(data),
        headers={
            'Content-Type': 'application/json',
            'X-Request-Id': str(random.randint(1, 1000)),
        },
    )
    response_data = json.loads(response.data)
    assert response.status_code == expected_answer['status']
    assert response_data['message'] == expected_answer['message']
    with app.app_context():
        test_user = db_session.query(User).filter_by(username='test_user').first()
        if test_user:
            db_session.delete(test_user)
            db_session.commit()


@pytest.mark.parametrize(
    'data, expected_answer',
    [
        (
            {
                'username': 'ivan.ivanov',
                'password': 'ivanov666',
            },
            {
                'status': HTTPStatus.OK,
                'message': 'Login successful'
            },
        ),
        (
            {
                'username': 'ivan.ivanov',
                'password': 'ivanov777',
            },
            {
                'status': HTTPStatus.UNAUTHORIZED,
                'message': 'Invalid username or password'
            },
        ),
        (
            {
                'username': 'ivan.ivanov',
                'new_password': 'ivanov777',
            },
            {
                'status': HTTPStatus.BAD_REQUEST,
                'message': 'Invalid input parameters'
            },
        ),
    ],
)
def test_login(data, expected_answer):
    tester = app.test_client()
    new_user = {
        'username': 'ivan.ivanov',
        'password': 'ivanov666',
        'email': 'ivan@ivanov.com',
    }
    response = tester.post(
        'api/v1/auth/register',
        data=json.dumps(new_user),
        headers={
            'Content-Type': 'application/json',
            'X-Request-Id': str(random.randint(1, 1000)),
        },
    )
    logger.info('Just created user: %s', new_user)
    logger.info('DATA: %s', data)
    response = tester.post(
        'api/v1/auth/login',
        data=json.dumps(data),
        headers={
            'Content-Type': 'application/json',
            'X-Request-Id': str(random.randint(1, 1000)),
        },
    )
    response_data = json.loads(response.data)
    assert response.status_code == expected_answer['status']
    if response.status_code == HTTPStatus.OK:
        assert response_data['access_token'] is not None
        assert response_data['refresh_token'] is not None
    else:
        assert response_data['message'] == expected_answer['message']


@pytest.mark.parametrize(
    'data, expected_answer',
    [
        (
            {
                'new_password': 'newP@ssworD666',
            },
            {
                'status': HTTPStatus.OK,
                'message': 'Password reset successfully'
            },
        ),
    ],
)
def test_password_reset(data, expected_answer):
    tester = app.test_client()
    new_user = {
        'username': 'ivan.ivanov',
        'password': 'ivanov666',
        'email': 'ivan@ivanov.com',
    }
    response = tester.post(
        'api/v1/auth/register',
        data=json.dumps(new_user),
        headers={
            'Content-Type': 'application/json',
            'X-Request-Id': str(random.randint(1, 1000)),
        },
    )
    logger.info('Just created user: %s', new_user)
    response = tester.post(
        'api/v1/auth/login',
        data=json.dumps({
            'username': 'ivan.ivanov',
            'password': 'ivanov666',
        }),
        headers={
            'Content-Type': 'application/json',
            'X-Request-Id': str(random.randint(1, 1000)),
        },
    )
    response_data = json.loads(response.data)
    assert response.status_code == HTTPStatus.OK
    assert response_data['access_token'] is not None
    assert response_data['refresh_token'] is not None
    response = tester.post(
        'api/v1/auth/password-reset',
        data=json.dumps({
            'new_password': data['new_password'],
        }),
        headers={
            'Authorization': f'Bearer {response_data["access_token"]}',
            'Content-Type': 'application/json',
            'X-Request-Id': str(random.randint(1, 1000)),
        },
        follow_redirects=False,
    )
    response_data = json.loads(response.data)
    assert response.status_code == expected_answer['status']
    assert response_data['message'] == expected_answer['message']
    response = tester.post(
        'api/v1/auth/login',
        data=json.dumps({
            'username': 'ivan.ivanov',
            'password': data['new_password'],
        }),
        headers={
            'Content-Type': 'application/json',
            'X-Request-Id': str(random.randint(1, 1000)),
        },
    )
    response_data = json.loads(response.data)
    assert response.status_code == HTTPStatus.OK
    assert response_data['access_token'] is not None
    assert response_data['refresh_token'] is not None


def test_logout():
    tester = app.test_client()
    new_user = {
        'username': 'ivan.ivanov',
        'password': 'ivanov666',
        'email': 'ivan@ivanov.com',
    }
    response = tester.post(
        'api/v1/auth/register',
        data=json.dumps(new_user),
        headers={
            'Content-Type': 'application/json',
            'X-Request-Id': str(random.randint(1, 1000)),
        },
    )
    logger.info('Just created user: %s', new_user)
    response = tester.post(
        'api/v1/auth/login',
        data=json.dumps({
            'username': 'ivan.ivanov',
            'password': 'ivanov666',
        }),
        headers={
            'Content-Type': 'application/json',
            'X-Request-Id': str(random.randint(1, 1000)),
        },
    )
    response_data = json.loads(response.data)
    assert response.status_code == HTTPStatus.OK
    assert response_data['access_token'] is not None
    assert response_data['refresh_token'] is not None
    access_token = response_data['access_token']
    response = tester.post(
        'api/v1/auth/logout',
        headers={
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json',
            'X-Request-Id': str(random.randint(1, 1000)),
        },
    )
    response_data = json.loads(response.data)
    assert response.status_code == HTTPStatus.OK
    assert response_data['message'] == 'Logout successful, access_token revoked'
    response = tester.post(
        'api/v1/auth/login',
        data=json.dumps({
            'username': 'ivan.ivanov',
            'password': 'ivanov666',
        }),
        headers={
            'Content-Type': 'application/json',
            'X-Request-Id': str(random.randint(1, 1000)),
        },
    )
    response_data = json.loads(response.data)
    assert response.status_code == HTTPStatus.OK
    assert response_data['access_token'] is not None
    assert response_data['refresh_token'] is not None
    assert response_data['access_token'] != access_token


def test_expired_access_token():
    tester = app.test_client()
    new_user = {
        'username': 'ivan.ivanov',
        'password': 'ivanov666',
        'email': 'ivan@ivanov.com',
    }
    response = tester.post(
        'api/v1/auth/register',
        data=json.dumps(new_user),
        headers={
            'Content-Type': 'application/json',
            'X-Request-Id': str(random.randint(1, 1000)),
        },
    )
    assert response.status_code == HTTPStatus.OK
    logger.info('Just created user: %s', new_user)
    response = tester.post(
        'api/v1/auth/login',
        data=json.dumps({
            'username': 'ivan.ivanov',
            'password': 'ivanov666',
        }),
        headers={
            'Content-Type': 'application/json',
            'X-Request-Id': str(random.randint(1, 1000)),
        },
    )
    assert response.status_code == HTTPStatus.OK
    response_data = json.loads(response.data)
    assert response_data['access_token'] is not None
    assert response_data['refresh_token'] is not None
    refresh_token = response_data['refresh_token']
    access_token = response_data['access_token']
    payload = jwt.decode(access_token, settings.secret_key, algorithms=['HS256'])
    payload['exp'] = time.time() - 10
    expired_token = jwt.encode(payload, settings.secret_key, algorithm='HS256')
    with app.app_context():
        token_storage = TokenStorage()
        token_storage.redis.set(expired_token, 'expired_token', ex=1)
    response = tester.post(
        'api/v1/auth/logout',
        headers={
            'Authorization': f'Bearer {expired_token}',
            'Content-Type': 'application/json',
            'X-Request-Id': str(random.randint(1, 1000)),
        },
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    response_data = json.loads(response.data)
    assert response_data['msg'] == 'Token has expired'
    response = tester.get(
        'api/v1/auth/refresh',
        headers={
            'Authorization': f'Bearer {refresh_token}',
            'Content-Type': 'application/json',
            'X-Request-Id': str(random.randint(1, 1000)),
        },
    )
    assert response.status_code == HTTPStatus.OK
    response_data = json.loads(response.data)
    assert response_data['access_token'] is not None
    new_access_token = response_data['access_token']
    assert new_access_token != access_token
