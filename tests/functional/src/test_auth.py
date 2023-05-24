import pytest
from flask import json
from http import HTTPStatus

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

    response = tester.post('api/v1/auth/register', data=json.dumps(data), content_type='application/json')
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
                'username': 'super.arnold',
                'password': '123qwe',
            },
            {
                'status': HTTPStatus.OK,
                'message': 'Login successful'
            },
        ),
    ],
)
def test_login(data, expected_answer):
    tester = app.test_client()

    logger.info('DATA: %s', data)

    response = tester.post('api/v1/auth/login', data=json.dumps(data), content_type='application/json')
    response_data = json.loads(response.data)
    
    assert response.status_code == expected_answer['status']
    assert response_data['message'] == expected_answer['message']
