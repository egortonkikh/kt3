"""Базовый класс для работы с REST API.

Реализация расширяет исходный класс BaseRequest из репозитория
https://github.com/sadboy2001/api_testing (папка api_testing, файл base_request.py):

* добавлена поддержка метода PUT (нужен для обновления сущностей);
* параметр endpoint_id сделан опциональным И может быть составным
  (например 'octocat/Hello-World' или 'octocat/Hello-World/contributors'),
  чтобы корректно работать с путями GitHub API вида /repos/{owner}/{repo}/...;
* в POST/PUT тело передаётся как JSON;
* добавлена защита от бесконечного цикла при сетевых ошибках;
* добавлена безопасная обработка ответов без JSON-тела;
* добавлен retry с экспоненциальной задержкой на транзитные ошибки (403/429/5xx);
* добавлены заголовки Accept и User-Agent (GitHub API требует User-Agent).
"""
import random
import time

import requests
import pprint


class BaseRequest:
    """Обёртка над requests для единообразной работы с API."""

    MAX_RETRIES = 6
    BASE_DELAY = 1.0  # базовая задержка между попытками (сек), растёт экспоненциально
    # Транзитные ошибки, которые надо ретраить.
    # ВАЖНО: 403 НЕ включён — у GitHub API 403 это всегда rate limit или
    # недостаток прав, ретраить бесполезно (только быстрее сжигаем лимит).
    TRANSIENT_STATUSES = {429, 500, 502, 503, 504}
    # Успешные HTTP-статусы
    SUCCESS_STATUSES = {200, 201}

    def __init__(self, base_url):
        self.base_url = base_url
        # set headers, authorisation etc
        self.session = requests.Session()
        self.session.headers.update({
            # GitHub API требует User-Agent, иначе возвращает 403.
            'User-Agent': 'api_testing/1.0 (python-requests)',
            'Accept': 'application/vnd.github+json',
        })

    def _request(self, url, request_type, data=None, expected_error=False):
        """Выполняет HTTP-запрос и логирует результат.

        Параметры:
            url            - полный адрес запроса;
            request_type   - 'GET' | 'POST' | 'PUT' | 'DELETE';
            data           - тело запроса (словарь), передаётся как JSON;
            expected_error - если True, метод не пытается повторить запрос
                             при ожидаемой неуспешной операции (404 и т.п.).
                             Транзитные ошибки (403/429/5xx) всё равно ретраятся.
        """
        stop_flag = False
        retries = 0
        response = None
        while not stop_flag:
            if request_type == 'GET':
                response = self.session.get(url, timeout=30)
            elif request_type == 'POST':
                response = self.session.post(url, json=data, timeout=30)
            elif request_type == 'PUT':
                response = self.session.put(url, json=data, timeout=30)
            elif request_type == 'DELETE':
                response = self.session.delete(url, timeout=30)
            else:
                raise ValueError(f'Unsupported request type: {request_type}')

            retries += 1
            transient = response.status_code in self.TRANSIENT_STATUSES

            if not expected_error and response.status_code in self.SUCCESS_STATUSES:
                # успех
                stop_flag = True
            elif expected_error and not transient:
                # ожидаемая ошибка (например 404) — фиксируем её
                stop_flag = True
            elif retries >= self.MAX_RETRIES:
                # исчерпали попытки — выходим, чтобы не зациклиться
                stop_flag = True
            else:
                # транзитная ошибка — экспоненциальная задержка с джиттером
                delay = self.BASE_DELAY * (2 ** (retries - 1)) + random.random()
                print(f'  -> {response.status_code} {response.reason}, '
                      f'повтор через {delay:.1f} с (попытка {retries}/{self.MAX_RETRIES})')
                time.sleep(delay)

            # log part
            pprint.pprint(f'{request_type} example')
            pprint.pprint(response.url)
            pprint.pprint(response.status_code)
            pprint.pprint(response.reason)
            pprint.pprint(response.text)
            try:
                pprint.pprint(response.json())
            except ValueError:
                pprint.pprint('No JSON body')
            pprint.pprint('**********')

        return response

    @staticmethod
    def _safe_json(response):
        """Парсит JSON ответа; если тела нет — возвращает заглушку-словарь."""
        try:
            return response.json()
        except ValueError:
            return {
                'code': response.status_code,
                'type': 'error',
                'message': (response.text or response.reason)[:200],
            }

    def _build_url(self, endpoint, endpoint_id=None):
        """Собирает URL. endpoint_id может быть составным, например
        'octocat/Hello-World/contributors' для /repos/octocat/Hello-World/contributors."""
        url = f'{self.base_url}/{endpoint}'
        if endpoint_id is not None:
            url = f'{url}/{endpoint_id}'
        return url

    def get(self, endpoint, endpoint_id=None, expected_error=False):
        url = self._build_url(endpoint, endpoint_id)
        response = self._request(url, 'GET', expected_error=expected_error)
        return self._safe_json(response)

    def post(self, endpoint, endpoint_id=None, body=None):
        url = self._build_url(endpoint, endpoint_id)
        response = self._request(url, 'POST', data=body)
        return self._safe_json(response)

    def put(self, endpoint, endpoint_id, body=None):
        url = self._build_url(endpoint, endpoint_id)
        response = self._request(url, 'PUT', data=body)
        return self._safe_json(response)

    def delete(self, endpoint, endpoint_id=None):
        url = self._build_url(endpoint, endpoint_id)
        response = self._request(url, 'DELETE')
        return self._safe_json(response)
