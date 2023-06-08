from os import getenv

from pydantic import AnyUrl, BaseModel
from dotenv import load_dotenv


load_dotenv()


class OAuthProviderConfig(BaseModel):
    provider_name: str
    client_id: str
    client_secret: str
    authorize_url: AnyUrl
    access_token_url: AnyUrl
    api_base_url: AnyUrl

    class Config:
        env_file = '.env'


class VKConfig(OAuthProviderConfig):
    provider_name: str = 'vk'


class YandexConfig(OAuthProviderConfig):
    provider_name: str = 'yandex'


vk_config = VKConfig(**{
    'provider_name': 'vk',
    'client_id': getenv('VK_CLIENT_ID'),
    'client_secret': getenv('VK_CLIENT_SECRET'),
    'authorize_url': 'https://oauth.vk.com/authorize',
    'access_token_url': 'https://oauth.vk.com/access_token',
    'api_base_url': 'https://api.vk.com/method/'
})

yandex_config = YandexConfig(**{
    'provider_name': 'yandex',
    'client_id': getenv('YANDEX_CLIENT_ID'),
    'client_secret': getenv('YANDEX_CLIENT_SECRET'),
    'authorize_url': 'https://oauth.yandex.com/authorize',
    'access_token_url': 'https://oauth.yandex.com/token',
    'api_base_url': 'https://login.yandex.ru/'
})
