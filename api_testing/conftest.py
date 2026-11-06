"""Pytest-фикстуры для тестов GitHub API.

Следует паттерну из исходного репозитория sadboy2001/api_testing
(ddt/test_parametrizations.py): фикстура base_url + клиентский объект.
"""
import pytest

from base_request import BaseRequest


BASE_URL_GITHUB = 'https://api.github.com'


@pytest.fixture(scope='session')
def base_url():
    """Базовый URL тестируемого API."""
    return BASE_URL_GITHUB


@pytest.fixture(scope='session')
def api_client(base_url):
    """Клиент API — экземпляр BaseRequest, разделяемый между всеми тестами."""
    return BaseRequest(base_url)


@pytest.fixture
def sample_username():
    """Известный публичный пользователь GitHub для тестов.
    'octocat' — маскот GitHub, всегда существует."""
    return 'octocat'


@pytest.fixture
def sample_repo():
    """Известный публичный репозиторий для тестов.
    octocat/Spoon-Knife — классический demo-репозиторий GitHub, небольшой,
    гарантированно имеет и контрибьюторов, и языки."""
    return {'owner': 'octocat', 'repo': 'Spoon-Knife'}


def skip_if_rate_limited(response):
    """Пропускает тест, если GitHub API вернул ошибку rate limit.

    GitHub возвращает 403 с телом:
    {"message": "API rate limit exceeded for ...", "documentation_url": "..."}
    Поэтому проверяем и поле 'code' (Petstore-стиль), и поле 'message'
    (GitHub-стиль).
    """
    if not isinstance(response, dict):
        return
    message = (response.get('message') or '').lower()
    if response.get('code') == 403 or 'rate limit' in message:
        pytest.skip(
            'GitHub API rate limit превышен (60 запросов/час для анонимных). '
            'Подождите до сброса лимита или используйте персональный токен.'
        )
