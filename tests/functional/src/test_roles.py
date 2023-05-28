from http import HTTPStatus
import pytest

from flask import json

from src.app import app
from src.db.db_config import db_session
from src.db.model import Role
from src.logs.log_config import logger


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


def make_authenticated_post(
        authenticated_client,
        url,
        data=None,
        content_type='application/json',
        headers=None,
):
    headers = headers or {}
    headers['Authorization'] = f'Bearer {authenticated_client.access_token}'
    return authenticated_client.post(
        url,
        data=data,
        content_type=content_type,
        headers=headers,
    )


def make_authenticated_put(
        authenticated_client,
        url,
        data=None,
        content_type='application/json',
        headers=None,
):
    headers = headers or {}
    headers['Authorization'] = f'Bearer {authenticated_client.access_token}'
    return authenticated_client.put(
        url,
        data=data,
        content_type=content_type,
        headers=headers,
    )


def make_authenticated_delete(
        authenticated_client,
        url,
        data=None,
        content_type='application/json',
        headers=None,
):
    headers = headers or {}
    headers['Authorization'] = f'Bearer {authenticated_client.access_token}'
    return authenticated_client.delete(
        url,
        data=data,
        content_type=content_type,
        headers=headers,
    )


def test_list_roles(authenticated_client):
    response = authenticated_client.get(
        'api/v1/roles/',
        headers={'Authorization': f'Bearer {authenticated_client.access_token}'},
    )
    assert response.status_code == HTTPStatus.OK
    roles = json.loads(response.data)
    assert len(roles) == 4


def test_create_role(authenticated_client):
    response = make_authenticated_post(
        authenticated_client,
        'api/v1/roles/',
        data=json.dumps({'name': 'test_role'}),
    )
    assert response.status_code == HTTPStatus.CREATED
    response_data = json.loads(response.data)
    assert response_data['message'] == 'Role created successfully'
    response = authenticated_client.get(
        'api/v1/roles/',
        headers={'Authorization': f'Bearer {authenticated_client.access_token}'},
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
        headers={'Authorization': f'Bearer {authenticated_client.access_token}'},
    )
    assert response.status_code == HTTPStatus.OK
    roles = json.loads(response.data)
    expected_roles = ('superuser', 'admin', 'user', 'guest')
    got_roles = []
    for role in roles:
        response = authenticated_client.get(
            f'api/v1/roles/{role["id"]}',
            headers={'Authorization': f'Bearer {authenticated_client.access_token}'},
        )
        assert response.status_code == HTTPStatus.OK
        got_roles.append(role['name'])
    assert set(expected_roles) == set(got_roles)


def test_update_role(authenticated_client):
    response = make_authenticated_post(
        authenticated_client,
        'api/v1/roles/',
        data=json.dumps({'name': 'test_role'}),
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
    )
    assert response.status_code == HTTPStatus.OK
    response_data = json.loads(response.data)
    assert response_data['message'] == 'Role deleted successfully'
    with app.app_context():
        test_role = db_session.query(Role).filter_by(role_name='test_role').first()
        assert test_role is None
