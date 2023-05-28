import pytest
from http import HTTPStatus

from flask import json

from src.app import app
from src.db.db_config import db_session
from src.db.model import User
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
        content_type='application/json',
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
        content_type='application/json',
    )
    logger.info('Just created user: %s', new_user)
    logger.info('DATA: %s', data)
    response = tester.post(
        'api/v1/auth/login',
        data=json.dumps(data),
        content_type='application/json',
    )
    response_data = json.loads(response.data)
    assert response.status_code == expected_answer['status']
    if response.status_code == HTTPStatus.OK:
        assert response_data['access_token'] is not None
        assert response_data['refresh_token'] is not None
    else:
        assert response_data['message'] == expected_answer['message']
    with app.app_context():
        test_user = db_session.query(User).filter_by(username='ivan.ivanov').first()
        if test_user:
            db_session.delete(test_user)
            db_session.commit()
            logger.info('Deleted user %s', test_user)


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
        content_type='application/json',
    )
    logger.info('Just created user: %s', new_user)
    response = tester.post(
        'api/v1/auth/login',
        data=json.dumps({
            'username': 'ivan.ivanov',
            'password': 'ivanov666',
        }),
        content_type='application/json',
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
        content_type='application/json',
        headers={'Authorization': f'Bearer {response_data["access_token"]}'},
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
        content_type='application/json',
    )
    response_data = json.loads(response.data)
    assert response.status_code == HTTPStatus.OK
    assert response_data['access_token'] is not None
    assert response_data['refresh_token'] is not None
    with app.app_context():
        test_user = db_session.query(User).filter_by(username='ivan.ivanov').first()
        if test_user:
            db_session.delete(test_user)
            db_session.commit()
            logger.info('Deleted user %s', test_user)


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
        content_type='application/json',
    )
    logger.info('Just created user: %s', new_user)
    response = tester.post(
        'api/v1/auth/login',
        data=json.dumps({
            'username': 'ivan.ivanov',
            'password': 'ivanov666',
        }),
        content_type='application/json',
    )
    response_data = json.loads(response.data)
    assert response.status_code == HTTPStatus.OK
    assert response_data['access_token'] is not None
    assert response_data['refresh_token'] is not None
    access_token = response_data['access_token']
    response = tester.post(
        'api/v1/auth/logout',
        headers={'Authorization': f'Bearer {access_token}'},
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
        content_type='application/json',
    )
    response_data = json.loads(response.data)
    assert response.status_code == HTTPStatus.OK
    assert response_data['access_token'] is not None
    assert response_data['refresh_token'] is not None
    assert response_data['access_token'] != access_token
    with app.app_context():
        test_user = db_session.query(User).filter_by(username='ivan.ivanov').first()
        if test_user:
            db_session.delete(test_user)
            db_session.commit()
            logger.info('Deleted user %s', test_user)
