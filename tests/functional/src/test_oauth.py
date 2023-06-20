from http import HTTPStatus
from os import getenv
import random

from dotenv import load_dotenv

from src.app import app


load_dotenv()


def test_vk_login():
    tester = app.test_client()
    response = tester.get(
        'api/v1/oauth/login/vk',
        headers={
            'Content-Type': 'application/json',
            'X-Request-Id': str(random.randint(1, 1000)),
        },
    )
    assert response.status_code == HTTPStatus.FOUND
    location = response.location
    assert location is not None
    assert location.startswith('https://oauth.vk.com/authorize')
    assert f'client_id={getenv("VK_CLIENT_ID")}' in location


def test_yandex_login():
    tester = app.test_client()
    response = tester.get(
        'api/v1/oauth/login/yandex',
        headers={
            'Content-Type': 'application/json',
            'X-Request-Id': str(random.randint(1, 1000)),
        },
    )
    assert response.status_code == HTTPStatus.FOUND
    location = response.location
    assert location is not None
    assert location.startswith('https://oauth.yandex.com/authorize')
    assert f'client_id={getenv("YANDEX_CLIENT_ID")}' in location
