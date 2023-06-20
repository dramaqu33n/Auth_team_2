from time import sleep

from src.db.redis import TokenStorage, TokenType


def test_token_storage():
    token_storage = TokenStorage()
    user_id = '123'
    access_token = 'mock_access_token'
    user_agent = 'Mozilla/5.0'
    token_storage.store_token(
        TokenType.ACCESS,
        user_id,
        user_agent,
        access_token,
    )
    retrieved_token = token_storage.get_token(
        TokenType.ACCESS,
        user_id,
        user_agent,
    )
    assert retrieved_token == access_token.encode()


def test_ttl():
    token_storage = TokenStorage()
    user_id = '123'
    access_token = 'mock_access_token'
    user_agent = 'Mozilla/5.0'
    token_storage.store_token(
        TokenType.ACCESS,
        user_id,
        user_agent,
        access_token,
        ttl=1,
    )
    sleep(2)
    retrieved_token = token_storage.get_token(
        TokenType.ACCESS,
        user_id,
        user_agent,
    )
    assert retrieved_token is None
