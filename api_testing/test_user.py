"""Тесты сущности users GitHub API (https://api.github.com).

4 запроса, реализованные как pytest-тесты через базовый класс BaseRequest:

1. GET /users                       - список пользователей;
2. GET /users/{username}            - получить пользователя по логину;
3. GET /users/{username}/repos      - список репозиториев пользователя;
4. GET /users/{username}/followers  - список подписчиков пользователя.
"""
import pytest

from conftest import skip_if_rate_limited


class TestUser:
    """Тесты сущности users GitHub API."""

    def test_list_users(self, api_client):
        """1. GET /users - список пользователей."""
        users = api_client.get('users')
        skip_if_rate_limited(users)

        assert isinstance(users, list), \
            f'Ожидается список, получено {type(users)}'
        assert len(users) > 0, 'Список пользователей не должен быть пустым'
        # Каждый элемент должен иметь поле login
        assert all('login' in u for u in users), \
            'Каждый пользователь должен иметь поле login'

    def test_get_user(self, api_client, sample_username):
        """2. GET /users/{username} - получить пользователя по логину."""
        user = api_client.get('users', sample_username)
        skip_if_rate_limited(user)

        assert user.get('login') == sample_username, \
            f'Ожидается login={sample_username}, получено {user.get("login")}'
        assert user.get('type') == 'User', \
            f'Ожидается type=User, получено {user.get("type")}'
        assert 'id' in user, 'У пользователя должно быть поле id'

    @pytest.mark.parametrize('sub_resource, expected_type', [
        ('repos', list),       # 3. GET /users/{username}/repos
        ('followers', list),   # 4. GET /users/{username}/followers
    ], ids=['repos', 'followers'])
    def test_user_subresources(self, api_client, sample_username,
                                sub_resource, expected_type):
        """3, 4. GET /users/{username}/{repos|followers}.

        Параметризация проверяет разные подресурсы пользователя, как в
        ddt/test_parametrizations.py с ids=...
        """
        result = api_client.get('users', f'{sample_username}/{sub_resource}')
        skip_if_rate_limited(result)

        assert isinstance(result, expected_type), \
            f'Ожидается {expected_type.__name__}, получено {type(result).__name__}'
