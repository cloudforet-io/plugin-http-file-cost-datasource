import logging
import time
import requests
import copy
import zlib
import pandas as pd
import numpy as np
from datetime import datetime
from io import StringIO

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
_PAGE_SIZE = 1000


class HTTPFileConnector(BaseConnector):

    def __init__(self, transaction: Transaction, config: dict):
        super().__init__(transaction, config)
        self.base_url = None
        self.http_headers = copy.deepcopy(_DEFAULT_HTTP_HEADERS)

    def create_session(self, options: dict, secret_data: dict, schema: str = None) -> None:
        self._check_options(options)
        self.base_url = options['base_url']

    def get_cost_data(self, base_url):
        _LOGGER.debug(f'[get_cost_data] base url: {base_url}')

        # costs_data = self._download_cost_data(base_url)
        costs_data = self._get_csv(base_url)
        print(costs_data)

        _LOGGER.debug(f'[get_cost_data] costs count: {len(costs_data)}')

        # Paginate
        page_count = int(len(costs_data) / _PAGE_SIZE) + 1

        for page_num in range(page_count):
            offset = _PAGE_SIZE * page_num
            yield costs_data[offset:offset + _PAGE_SIZE]

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

    @staticmethod
    def _download_cost_data(base_url: str) -> str:
        try:
            response = requests.get(base_url)
            cost_bytes = zlib.decompress(response.content, zlib.MAX_WBITS | 32)
            return cost_bytes.decode('utf-8')
        except Exception as e:
            _LOGGER.error(f'[_download_cost_data] download error: {e}', exc_info=True)
            raise e

    @staticmethod
    def _get_csv(base_url: str) -> list[dict]:
        try:
            df = pd.read_csv(base_url)
            df = df.replace({np.nan: None})

            costs_data = df.to_dict('records')
            return costs_data
        except Exception as e:
            _LOGGER.error(f'[_get_csv] download error: {e}', exc_info=True)
            raise e
