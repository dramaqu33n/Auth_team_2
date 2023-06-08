from http import HTTPStatus
import jwt
from os import getenv
import pytest
import time
from urllib.parse import urlparse, parse_qs

from flask import json
from dotenv import load_dotenv

from src.app import app
from src.core.config import settings
from src.db.db_config import db_session
from src.db.model import User
from src.db.redis import TokenStorage, TokenType
from src.logs.log_config import logger


load_dotenv()


def test_vk_login():
    tester = app.test_client()
    response = tester.get('api/v1/oauth/login/vk')
    assert response.status_code == HTTPStatus.FOUND
    location = response.location
    assert location is not None
    assert location.startswith('https://oauth.vk.com/authorize')
    assert f'client_id={getenv("VK_CLIENT_ID")}' in location

def test_yandex_login():
    tester = app.test_client()
    response = tester.get('api/v1/oauth/login/yandex')
    assert response.status_code == HTTPStatus.FOUND
    location = response.location
    assert location is not None
    assert location.startswith('https://oauth.yandex.com/authorize')
    assert f'client_id={getenv("YANDEX_CLIENT_ID")}' in location
