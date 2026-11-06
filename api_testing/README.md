# КТ №3 - Тестирование API GitHub

Тестируемый API: **GitHub REST API** — https://api.github.com
Базовый класс взят за основу из репозитория: https://github.com/sadboy2001/api_testing
(папка `api_testing`, файл `base_request.py`).

## Внимание: про сущность store

В исходном задании упоминаются сущности `user` и `store`. У GitHub API **нет
сущности store** — ближайший аналог это `repos` (репозитории). Поэтому:

| Задание     | Здесь                | Причина                              |
|-------------|----------------------|--------------------------------------|
| user (×4)   | `test_user.py`       | В GitHub есть `/users`               |
| store (×4)  | `test_repos.py`      | В GitHub нет store; используем repos |


## Тестовые данные

Все тесты используют публичные объекты GitHub, которые гарантированно существуют:

| Фикстура         | Значение                  | Назначение                                |
|------------------|---------------------------|-------------------------------------------|
| `sample_username`| `octocat`                 | Маскот GitHub, есть в `/users/octocat`    |
| `sample_repo`    | `octocat/Spoon-Knife`     | Demo-репозиторий с контрибьюторами и языками |

## Структура проекта

Структура повторяет исходный репозиторий `sadboy2001/api_testing`
(папка `api_testing/` — клиентский код, тесты в стиле `ddt/`):

```
api_testing/
├── base_request.py        # базовый класс BaseRequest (GET/POST/PUT/DELETE)
├── conftest.py            # pytest-фикстуры: base_url, api_client, sample_username, sample_repo
├── test_user.py           # 4 pytest-теста для сущности users (класс TestUser)
├── test_repos.py          # 4 pytest-теста для сущности repos (класс TestRepos)
├── requests_example.py    # демо-скрипты без pytest (как requests_example.py из репо)
├── requirements.txt
└── README.md
```

## Установка

```bash
pip install -r requirements.txt
```

## Запуск тестов (pytest)

```bash
cd api_testing
pytest -v                 # все тесты
pytest test_user.py -v    # только тесты сущности user
pytest test_repos.py -v   # только тесты сущности repos
```

## Запуск демо-скриптов (без pytest)

```bash
python requests_example.py
```

## Что делает каждый тест

### test_user.py — сущность `users` (класс `TestUser`)

| № | Тест                      | Метод | Endpoint                          | Описание                          |
|---|---------------------------|-------|-----------------------------------|-----------------------------------|
| 1 | `test_list_users`         | GET   | `/users`                          | Список пользователей              |
| 2 | `test_get_user`           | GET   | `/users/{username}`               | Получить пользователя по логину   |
| 3 | `test_user_subresources`  | GET   | `/users/{username}/repos`         | Список репозиториев пользователя  |
| 4 | `test_user_subresources`  | GET   | `/users/{username}/followers`     | Список подписчиков пользователя   |

`test_user_subresources` параметризован по подресурсам (`repos`, `followers`)
с `ids=...` — паттерн из `ddt/test_parametrizations.py` исходного репозитория.

### test_repos.py — сущность `repos` (класс `TestRepos`)

| № | Тест                       | Метод | Endpoint                                  | Описание                       |
|---|----------------------------|-------|-------------------------------------------|--------------------------------|
| 1 | `test_list_public_repos`   | GET   | `/repositories`                           | Список публичных репозиториев  |
| 2 | `test_get_repo`            | GET   | `/repos/{owner}/{repo}`                   | Получить репозиторий           |
| 3 | `test_repo_subresources`   | GET   | `/repos/{owner}/{repo}/contributors`      | Список контрибьюторов          |
| 4 | `test_repo_subresources`   | GET   | `/repos/{owner}/{repo}/languages`         | Языки репозитория              |

`test_repo_subresources` параметризован по подресурсам (`contributors`,
`languages`) — паттерн из исходного репо.

## Соответствие стилю исходного репозитория

| Элемент                       | В исходном репо                            | Здесь                       |
|-------------------------------|--------------------------------------------|-----------------------------|
| Базовый класс                 | `api_testing/base_request.py`              | `base_request.py`           |
| Демо-скрипт без pytest        | `api_testing/requests_example.py`          | `requests_example.py`       |
| Pytest-тесты с фикстурой base_url | `ddt/test_parametrizations.py`         | `conftest.py` + `test_*.py` |
| Параметризация с `ids=`       | `test_with_ids`                            | `test_user_subresources`, `test_repo_subresources` |
| Тест-класс `class TestXxx`    | `TestParameterized` в `test_pairwise_example.py` | `TestUser`, `TestRepos` |

## Отличия от исходного base_request.py

Реализация сохраняет структуру и логику исходного класса, но с минимальными
доработками, необходимыми для работы с GitHub API:

1. **Добавлен метод `put`** — нужен для `PUT /repos/{owner}/{repo}` (обновление).
   В исходном классе были только GET/POST/DELETE.
2. **`endpoint_id` опционален и может быть составным** — это позволяет корректно
   формировать пути GitHub API вида `/repos/octocat/Hello-World/contributors`
   (передаётся как `endpoint_id='octocat/Hello-World/contributors'`).
3. **Тело POST/PUT передаётся как JSON** (`json=data`) — GitHub ожидает
   `application/json`.
4. **Защита от бесконечного цикла** — добавлен счётчик `MAX_RETRIES` и
   экспоненциальная задержка.
5. **Безопасный разбор JSON** — не у всех ответов есть тело.
6. **Заголовок `Accept: application/vnd.github+json`** — рекомендуется в
   документации GitHub API. Заголовок `User-Agent` обязателен (иначе 403).

## Если возникает 403 Forbidden (rate limit)

GitHub API для анонимных запросов ограничивает **60 запросов в час** по IP.
При превышении лимита тесты помечаются как `SKIPPED` с пояснением.

Решения:

1. **Подождать час** — лимит сбрасывается.
2. **Использовать персональный токен** — тогда лимит 5000 запросов/час.
   Создайте токен на https://github.com/settings/tokens (нужны права `public_repo`)
   и добавьте в `base_request.py`:
   ```python
   self.session.headers.update({'Authorization': 'Bearer ВАШ_ТОКЕН'})
   ```
3. **Запустить позже** с другого IP.
