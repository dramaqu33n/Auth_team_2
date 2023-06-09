from http import HTTPStatus
import random

from flask import json

from src.app import app
from src.db.db_config import db
from src.db.model import Role
from src.logs.log_config import logger
from tests.functional.utils import make_authenticated_delete
from tests.functional.utils import make_authenticated_post
from tests.functional.utils import make_authenticated_put


db_session = db.session


def test_list_roles(authenticated_client):
    response = authenticated_client.get(
        'api/v1/roles/',
        headers={
            'Authorization': f'Bearer {authenticated_client.access_token}',
            'Content-Type': 'application/json',
            'X-Request-Id': str(random.randint(1, 1000)),
        },
    )
    assert response.status_code == HTTPStatus.OK
    roles = json.loads(response.data)
    assert len(roles) == 4


def test_create_role(authenticated_client):
    response = make_authenticated_post(
        authenticated_client,
        'api/v1/roles/',
        data=json.dumps({'name': 'test_role'}),
        headers={
            'Content-Type': 'application/json',
            'X-Request-Id': str(random.randint(1, 1000)),
        },
    )
    if response.status_code == HTTPStatus.PERMANENT_REDIRECT:
        response = authenticated_client.get(
            response.headers['Location'],
            headers={
                'Authorization': f'Bearer {authenticated_client.access_token}',
                'Content-Type': 'application/json',
                'X-Request-Id': str(random.randint(1, 1000)),
            },
        )
    assert response.status_code == HTTPStatus.CREATED
    response_data = json.loads(response.data)
    assert response_data['message'] == 'Role created successfully'
    response = authenticated_client.get(
        'api/v1/roles/',
        headers={
            'Authorization': f'Bearer {authenticated_client.access_token}',
            'Content-Type': 'application/json',
            'X-Request-Id': str(random.randint(1, 1000)),
        },
    )
    assert response.status_code == HTTPStatus.OK
    roles = json.loads(response.data)
    assert len(roles) == 5
    with app.app_context():
        test_role = db_session.query(Role).filter_by(role_name='test_role').first()
        if test_role:
            db_session.delete(test_role)
            db_session.commit()
            logger.info('Deleted role %s', test_role)


def test_get_role(authenticated_client):
    response = authenticated_client.get(
        'api/v1/roles/',
        headers={
            'Authorization': f'Bearer {authenticated_client.access_token}',
            'Content-Type': 'application/json',
            'X-Request-Id': str(random.randint(1, 1000)),
        },
        follow_redirects=True,
    )
    if response.status_code == HTTPStatus.PERMANENT_REDIRECT:
        response = authenticated_client.get(
            response.headers['Location'],
            headers={
                'Authorization': f'Bearer {authenticated_client.access_token}',
                'Content-Type': 'application/json',
                'X-Request-Id': str(random.randint(1, 1000)),
            },
        )
    assert response.status_code == HTTPStatus.OK
    roles = json.loads(response.data)
    expected_roles = ('superuser', 'admin', 'user', 'guest')
    got_roles = []
    for role in roles:
        response = authenticated_client.get(
            f'api/v1/roles/{role["id"]}',
            headers={
                'Authorization': f'Bearer {authenticated_client.access_token}',
                'Content-Type': 'application/json',
                'X-Request-Id': str(random.randint(1, 1000)),
            },
        )
        assert response.status_code == HTTPStatus.OK
        got_roles.append(role['name'])
    assert set(expected_roles) == set(got_roles)


def test_update_role(authenticated_client):
    response = make_authenticated_post(
        authenticated_client,
        'api/v1/roles/',
        data=json.dumps({'name': 'test_role'}),
        headers={
            'Authorization': f'Bearer {authenticated_client.access_token}',
            'Content-Type': 'application/json',
            'X-Request-Id': str(random.randint(1, 1000)),
        },
    )
    if response.status_code == HTTPStatus.PERMANENT_REDIRECT:
        response = authenticated_client.get(
            response.headers['Location'],
            headers={
                'Authorization': f'Bearer {authenticated_client.access_token}',
                'Content-Type': 'application/json',
                'X-Request-Id': str(random.randint(1, 1000)),
            },
        )
    assert response.status_code == HTTPStatus.CREATED
    response_data = json.loads(response.data)
    assert response_data['message'] == 'Role created successfully'
    with app.app_context():
        test_role = db_session.query(Role).filter_by(role_name='test_role').first()
    role_id = str(test_role.id)
    response = make_authenticated_put(
        authenticated_client,
        f'api/v1/roles/{role_id}',
        data=json.dumps({'name': 'test_role'}),
        headers={
            'Authorization': f'Bearer {authenticated_client.access_token}',
            'Content-Type': 'application/json',
            'X-Request-Id': str(random.randint(1, 1000)),
        },
    )
    assert response.status_code == HTTPStatus.OK
    response_data = json.loads(response.data)
    assert response_data['message'] == 'Role updated successfully'
    with app.app_context():
        test_role = db_session.query(Role).filter_by(role_name='test_role').first()
        if test_role:
            db_session.delete(test_role)
            db_session.commit()
            logger.info('Deleted role %s', test_role)


def test_delete_role(authenticated_client):
    response = make_authenticated_post(
        authenticated_client,
        'api/v1/roles/',
        data=json.dumps({'name': 'test_role'}),
        headers={
            'Authorization': f'Bearer {authenticated_client.access_token}',
            'Content-Type': 'application/json',
            'X-Request-Id': str(random.randint(1, 1000)),
        },
    )
    if response.status_code == HTTPStatus.PERMANENT_REDIRECT:
        response = authenticated_client.get(
            response.headers['Location'],
            headers={
                'Authorization': f'Bearer {authenticated_client.access_token}',
                'Content-Type': 'application/json',
                'X-Request-Id': str(random.randint(1, 1000)),
            },
        )
    assert response.status_code == HTTPStatus.CREATED
    response_data = json.loads(response.data)
    assert response_data['message'] == 'Role created successfully'
    with app.app_context():
        test_role = db_session.query(Role).filter_by(role_name='test_role').first()
    role_id = str(test_role.id)
    response = make_authenticated_delete(
        authenticated_client,
        f'api/v1/roles/{role_id}',
        data=json.dumps({'name': 'test_role'}),
        headers={
            'Authorization': f'Bearer {authenticated_client.access_token}',
            'Content-Type': 'application/json',
            'X-Request-Id': str(random.randint(1, 1000)),
        },
    )
    assert response.status_code == HTTPStatus.OK
    response_data = json.loads(response.data)
    assert response_data['message'] == 'Role deleted successfully'
    with app.app_context():
        test_role = db_session.query(Role).filter_by(role_name='test_role').first()
        assert test_role is None
