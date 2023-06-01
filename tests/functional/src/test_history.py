from http import HTTPStatus

from flask import json


def test_all_history_permission_denied(authenticated_client):
    response = authenticated_client.get(
        'api/v1/history/all',
        headers={'Authorization': f'Bearer {authenticated_client.access_token}'},
        follow_redirects=True,
    )
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert json.loads(response.data)['message'] == 'Permission denied'


def test_all_history(authenticated_superuser):
    response = authenticated_superuser.get(
        'api/v1/history/all',
        headers={'Authorization': f'Bearer {authenticated_superuser.access_token}'},
        follow_redirects=True,
    )
    assert response.status_code == HTTPStatus.OK
    response_data = json.loads(response.data)
    assert len(response_data) > 0


def test_get_my_history(authenticated_client):
    response = authenticated_client.get(
        'api/v1/history/',
        headers={'Authorization': f'Bearer {authenticated_client.access_token}'},
        follow_redirects=True,
    )
    assert response.status_code == HTTPStatus.OK
    response_data = json.loads(response.data)
    assert len(response_data) > 0
    access_history_records = []
    access_history_user_ids = []
    for access_history_record in response_data:
        access_history_records.append(access_history_record['id'])
        access_history_user_ids.append(access_history_record['user_id'])
    assert len(set(access_history_records)) == len(response_data)
    assert len(set(access_history_user_ids)) == 1

def test_paginated_history(authenticated_superuser):
    response = authenticated_superuser.get(
        'api/v1/history/?page=1&per_page=5',
        headers={'Authorization': f'Bearer {authenticated_superuser.access_token}'},
        follow_redirects=True,
    )
    assert response.status_code == HTTPStatus.OK
    response_data = json.loads(response.data)
    assert len(response_data) == 5
