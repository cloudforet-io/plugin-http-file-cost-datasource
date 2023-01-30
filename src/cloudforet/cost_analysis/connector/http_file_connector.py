import logging
import time
import requests
import copy
import zlib
from datetime import datetime

from spaceone.core.transaction import Transaction
from spaceone.core.connector import BaseConnector
from typing import List

from cloudforet.cost_analysis.error import *

__all__ = ['HTTPFileConnector']

_LOGGER = logging.getLogger(__name__)

_DEFAULT_HTTP_HEADERS = {
    'Content-Type': 'application/json',
    'accept': 'application/json'
}


class HTTPFileConnector(BaseConnector):

    def __init__(self, transaction: Transaction, config: dict):
        super().__init__(transaction, config)
        self.base_url = None
        self.column_headers = None
        self.http_headers = copy.deepcopy(_DEFAULT_HTTP_HEADERS)

    def create_session(self, options: dict, secret_data: dict, schema: str = None) -> None:
        self._check_options(options)
        self.base_url = options['base_url']
        self.column_headers = options['column_headers']

    def get_cost_data(self, signed_url):
        _LOGGER.debug(f'[get_cost_data] download url: {signed_url}')

        cost_csv = self._download_cost_data(signed_url)

    def get_change_dates(self, start: datetime = None, last_synchronized_at: datetime = None) -> List[dict]:
        if start:
            last_sync_time = time.mktime(start.timetuple())
        elif last_synchronized_at:
            last_sync_time = time.mktime(last_synchronized_at.timetuple())
        else:
            last_sync_time = 0

        data = {
            'last_sync_timestamp': last_sync_time
        }

        _LOGGER.debug(f'[get_change_dates] {self.base_url} => {data}')

        response = requests.post(self.base_url, json=data, headers=self.http_headers)

        if response.status_code == 200:
            return response.json().get('results', [])
        else:
            _LOGGER.error(f'[get_change_dates] error code: {response.status_code}')
            try:
                error_message = response.json()
            except Exception as e:
                error_message = str(response)

            _LOGGER.error(f'[get_change_dates] error message: {error_message}')
            raise ERROR_CONNECTOR_CALL_API(reason=error_message)

    @staticmethod
    def _check_options(options: dict) -> None:
        if 'base_url' not in options:
            raise ERROR_REQUIRED_PARAMETER(key='options.base_url')

        if 'column_headers' not in options:
            raise ERROR_REQUIRED_PARAMETER(key='options.column_headers')

    @staticmethod
    def _download_cost_data(signed_url: str) -> str:
        try:
            response = requests.get(signed_url)
            cost_bytes = zlib.decompress(response.content, zlib.MAX_WBITS | 32)
            return cost_bytes.decode('utf-8')
        except Exception as e:
            _LOGGER.error(f'[_download_cost_data] download error: {e}', exc_info=True)
            raise e
