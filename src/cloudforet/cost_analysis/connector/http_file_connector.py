import logging
import pandas as pd
import numpy as np
import chardet
import requests
import google.oauth2.service_account

from spaceone.core.transaction import Transaction
from spaceone.core.connector import BaseConnector
from typing import List

from cloudforet.cost_analysis.error import *

__all__ = ["HTTPFileConnector"]

_LOGGER = logging.getLogger(__name__)

_PAGE_SIZE = 1000


class HTTPFileConnector(BaseConnector):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.base_url = None
        self.field_mapper = None
        self.default_vars = None

    def create_session(
        self, options: dict, secret_data: dict, schema: str = None
    ) -> None:
        self._check_options(options)
        self.base_url = options["base_url"]

        if "field_mapper" in options:
            self.field_mapper = options["field_mapper"]

        if "default_vars" in options:
            self.default_vars = options["default_vars"]

    def get_cost_data(self, base_url):
        _LOGGER.debug(f"[get_cost_data] base url: {base_url}")

        costs_data = self._get_csv(base_url)

        _LOGGER.debug(f"[get_cost_data] costs count: {len(costs_data)}")

        # Paginate
        page_count = int(len(costs_data) / _PAGE_SIZE) + 1

        for page_num in range(page_count):
            offset = _PAGE_SIZE * page_num
            yield costs_data[offset : offset + _PAGE_SIZE]

    @staticmethod
    def _check_options(options: dict) -> None:
        if "base_url" not in options:
            raise ERROR_REQUIRED_PARAMETER(key="options.base_url")

    def _get_csv(self, base_url: str) -> List[dict]:
        try:
            csv_format = self._search_csv_format(base_url)
            df = pd.read_csv(
                base_url,
                header=0,
                sep=",",
                engine="python",
                encoding=csv_format,
                dtype=str,
            )
            df = df.replace({np.nan: None})

            costs_data = df.to_dict("records")
            return costs_data

        except Exception as e:
            _LOGGER.error(f"[_get_csv] download error: {e}", exc_info=True)
            raise e

    @staticmethod
    def _search_csv_format(base_url: str) -> str:
        try:
            response = requests.get(base_url)
            response.encoding = chardet.detect(response.content)["encoding"]
            _LOGGER.debug(f"[_search_csv_format] encoding: {response.encoding}")
            return response.encoding

        except Exception as e:
            _LOGGER.error(f"[_search_csv_format] download error: {e}", exc_info=True)
            raise e
