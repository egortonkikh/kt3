"""Демо-скрипты запросов к GitHub API без pytest.

Аналог requests_example.py из исходного репозитория sadboy2001/api_testing:
запускается напрямую `python requests_example.py` и показывает по одному
примеру каждого запроса к сущностям user и repos.
"""
import pprint

from base_request import BaseRequest


BASE_URL_GITHUB = 'https://api.github.com'
base_request = BaseRequest(BASE_URL_GITHUB)

SAMPLE_USERNAME = 'octocat'
SAMPLE_REPO = {'owner': 'octocat', 'repo': 'Spoon-Knife'}


# --------------------------------------------------------------------------- #
# Сущность USER: 4 запроса
# --------------------------------------------------------------------------- #
print('\n' + '=' * 70)
print('USER: 4 запроса')
print('=' * 70)

# 1. GET /users - список пользователей
print('\n--- 1. GET /users ---')
users = base_request.get('users')
pprint.pprint(users[:2] if isinstance(users, list) else users)

# 2. GET /users/{username} - получить пользователя по логину
print('\n--- 2. GET /users/{username} ---')
user = base_request.get('users', SAMPLE_USERNAME)
pprint.pprint(user)

# 3. GET /users/{username}/repos - список репозиториев пользователя
print('\n--- 3. GET /users/{username}/repos ---')
user_repos = base_request.get('users', f'{SAMPLE_USERNAME}/repos')
pprint.pprint(user_repos[:2] if isinstance(user_repos, list) else user_repos)

# 4. GET /users/{username}/followers - список подписчиков
print('\n--- 4. GET /users/{username}/followers ---')
followers = base_request.get('users', f'{SAMPLE_USERNAME}/followers')
pprint.pprint(followers[:2] if isinstance(followers, list) else followers)


# --------------------------------------------------------------------------- #
# Сущность REPOS (аналог store): 4 запроса
# --------------------------------------------------------------------------- #
print('\n' + '=' * 70)
print('REPOS: 4 запроса')
print('=' * 70)

# 1. GET /repositories - список публичных репозиториев
print('\n--- 1. GET /repositories ---')
repos = base_request.get('repositories')
pprint.pprint(repos[:2] if isinstance(repos, list) else repos)

# 2. GET /repos/{owner}/{repo} - получить репозиторий
print('\n--- 2. GET /repos/{owner}/{repo} ---')
repo_path = f"{SAMPLE_REPO['owner']}/{SAMPLE_REPO['repo']}"
repo = base_request.get('repos', repo_path)
pprint.pprint(repo)

# 3. GET /repos/{owner}/{repo}/contributors - список контрибьюторов
print('\n--- 3. GET /repos/{owner}/{repo}/contributors ---')
contributors = base_request.get('repos', f'{repo_path}/contributors')
pprint.pprint(contributors[:2] if isinstance(contributors, list) else contributors)

# 4. GET /repos/{owner}/{repo}/languages - список языков
print('\n--- 4. GET /repos/{owner}/{repo}/languages ---')
languages = base_request.get('repos', f'{repo_path}/languages')
pprint.pprint(languages)

print('\nГотово.')
