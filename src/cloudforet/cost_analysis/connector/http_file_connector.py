import logging
import copy
import pandas as pd
import numpy as np

from spaceone.core.transaction import Transaction
from spaceone.core.connector import BaseConnector
from cloudforet.cost_analysis.error import *

__all__ = ['HTTPFileConnector']

_LOGGER = logging.getLogger(__name__)

_DEFAULT_CSV_COLUMNS = [
    'cost',
    'currency',
    'usage_quantity',
    'provider',
    'region_code',
    'product',
    'account',
    'year',
    'month',
    'day'
]

_PAGE_SIZE = 1000


class HTTPFileConnector(BaseConnector):

    def __init__(self, transaction: Transaction, config: dict):
        super().__init__(transaction, config)
        self.base_url = None

    def create_session(self, options: dict, secret_data: dict, schema: str = None) -> None:
        self._check_options(options)
        self.base_url = options['base_url']

    def get_cost_data(self, base_url):
        _LOGGER.debug(f'[get_cost_data] base url: {base_url}')

        costs_data = self._get_csv(base_url)

        _LOGGER.debug(f'[get_cost_data] costs count: {len(costs_data)}')

        # Paginate
        page_count = int(len(costs_data) / _PAGE_SIZE) + 1

        for page_num in range(page_count):
            offset = _PAGE_SIZE * page_num
            yield costs_data[offset:offset + _PAGE_SIZE]

    @staticmethod
    def _check_options(options: dict) -> None:
        if 'base_url' not in options:
            raise ERROR_REQUIRED_PARAMETER(key='options.base_url')

    def _get_csv(self, base_url: str) -> list[dict]:
        try:
            df = pd.read_csv(base_url)
            df = df.replace({np.nan: None})

            self._check_columns(df)

            costs_data = df.to_dict('records')
            return costs_data
        except Exception as e:
            _LOGGER.error(f'[_get_csv] download error: {e}', exc_info=True)
            raise e

    @staticmethod
    def _check_columns(data_frame):
        for column in data_frame.columns:
            if column not in _DEFAULT_CSV_COLUMNS:
                _LOGGER.error(f'[_check_columns] invalid columns: {column}', exc_info=True)
                raise ERROR_INVALID_PARAMETER(key=column)
