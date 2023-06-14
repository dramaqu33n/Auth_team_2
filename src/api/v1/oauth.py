from datetime import timedelta
from http import HTTPStatus

from authlib.integrations.flask_client import OAuth
from flask import Blueprint, jsonify, request
from flask import url_for
from flask_jwt_extended import create_refresh_token
from flask_jwt_extended import get_jwt_identity

from src.core.oauth_providers import OAuthProviderConfig
from src.core.oauth_providers import vk_config, yandex_config
from src.db.redis import TokenStorage, TokenType


oauth_bp = Blueprint('oauth', __name__)
oauth = OAuth()
token_storage = TokenStorage()


def create_oauth_provider(provider: OAuthProviderConfig):
    oauth.register(
        name=provider.provider_name,
        client_id=provider.client_id,
        client_secret=provider.client_secret,
        authorize_url=provider.authorize_url,
        access_token_url=provider.access_token_url,
        api_base_url=provider.api_base_url
    )
    return oauth


oauth = create_oauth_provider(vk_config)
oauth = create_oauth_provider(yandex_config)


@oauth_bp.route('/login/<provider_name>', methods=['GET'])
def oauth_login(provider_name):
    callback_url = url_for(
        'api_v1.oauth.oauth_callback',
        provider=provider_name,
        _external=True,
    )
    provider = oauth.create_client(provider_name)
    resp = provider.authorize_redirect(callback=callback_url)
    return resp


@oauth_bp.route('/callback', methods=['GET'])
def oauth_callback():
    provider_name = request.args.get('provider')
    provider = oauth.create_client(provider_name)
    token = provider.authorize_access_token()
    if 'error' in token:
        return jsonify({'message': 'OAuth authorization failed'}), HTTPStatus.UNAUTHORIZED
    access_token = token['access_token']
    expires_in = token['expires_in']
    user_agent = request.headers.get('User-Agent')
    user_id = get_jwt_identity()
    token_storage.store_token(
        TokenType.ACCESS,
        str(user_id),
        user_agent,
        access_token,
        ttl=expires_in,
    )
    refresh_token = create_refresh_token(
        identity=str(user_id),
        expires_delta=timedelta(days=expires_in * 10),
    )
    token_storage.store_token(
        TokenType.REFRESH,
        str(user_id),
        user_agent,
        refresh_token,
        ttl=expires_in * 10,
    )
    return jsonify({'message': 'OAuth authorization successful'}), HTTPStatus.OK
