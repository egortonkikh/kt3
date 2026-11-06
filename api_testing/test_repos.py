"""Тесты сущности repos GitHub API (https://api.github.com).

4 запроса, реализованные как pytest-тесты через базовый класс BaseRequest:

1. GET /repositories                          - список публичных репозиториев;
2. GET /repos/{owner}/{repo}                  - получить репозиторий по owner/repo;
3. GET /repos/{owner}/{repo}/contributors     - список контрибьюторов;
4. GET /repos/{owner}/{repo}/languages        - список языков репозитория.
"""
import pytest

from conftest import skip_if_rate_limited


class TestRepos:
    """Тесты сущности repos GitHub API."""

    def test_list_public_repos(self, api_client):
        """1. GET /repositories - список публичных репозиториев."""
        repos = api_client.get('repositories')
        skip_if_rate_limited(repos)

        assert isinstance(repos, list), \
            f'Ожидается список, получено {type(repos)}'
        assert len(repos) > 0, 'Список репозиториев не должен быть пустым'
        # Каждый элемент должен иметь поля name и owner
        assert all('name' in r and 'owner' in r for r in repos), \
            'Каждый репозиторий должен иметь поля name и owner'

    def test_get_repo(self, api_client, sample_repo):
        """2. GET /repos/{owner}/{repo} - получить репозиторий."""
        repo_path = f"{sample_repo['owner']}/{sample_repo['repo']}"
        repo = api_client.get('repos', repo_path)
        skip_if_rate_limited(repo)

        assert repo.get('name') == sample_repo['repo'], \
            f'Ожидается name={sample_repo["repo"]}, получено {repo.get("name")}'
        assert repo.get('owner', {}).get('login') == sample_repo['owner'], \
            f'Ожидается owner.login={sample_repo["owner"]}, ' \
            f'получено {repo.get("owner", {}).get("login")}'
        assert 'id' in repo, 'У репозитория должно быть поле id'
        assert 'full_name' in repo, 'У репозитория должно быть поле full_name'

    @pytest.mark.parametrize('sub_resource, expected_type, description', [
        ('contributors', list, 'список контрибьюторов'),    # 3
        ('languages', dict, 'языки репозитория'),           # 4
    ], ids=['contributors', 'languages'])
    def test_repo_subresources(self, api_client, sample_repo,
                                sub_resource, expected_type, description):
        """3, 4. GET /repos/{owner}/{repo}/{contributors|languages}.

        Параметризация проверяет разные подресурсы репозитория.
        """
        repo_path = f"{sample_repo['owner']}/{sample_repo['repo']}/{sub_resource}"
        result = api_client.get('repos', repo_path)
        skip_if_rate_limited(result)

        assert isinstance(result, expected_type), \
            f'Ожидается {expected_type.__name__} ({description}), ' \
            f'получено {type(result).__name__}'

        if sub_resource == 'contributors':
            assert len(result) > 0, 'Список контрибьюторов не должен быть пустым'
            assert all('login' in c for c in result), \
                'Каждый контрибьютор должен иметь поле login'
        elif sub_resource == 'languages':
            # У репозитория может быть 0 языков (пустой репозиторий), но
            # для torvalds/linux языки гарантированно есть.
            assert all(isinstance(k, str) and isinstance(v, int)
                       for k, v in result.items()), \
                'Языки должны быть {название: количество_байтов}'
