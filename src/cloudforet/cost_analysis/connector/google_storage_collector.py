import os
import logging
import pandas as pd
import numpy as np
import tempfile
from typing import List
import google.oauth2.service_account
from google.cloud import storage
from cloudforet.cost_analysis.error import *
from spaceone.core.connector import BaseConnector

_PAGE_SIZE = 1000

_LOGGER = logging.getLogger("spaceone")


class GoogleStorageConnector(BaseConnector):
    google_client_service = "storage"
    version = "v1"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.secret_data = kwargs.get("secret_data")
        self.project_id = self.secret_data.get("project_id")
        self.credentials = (
            google.oauth2.service_account.Credentials.from_service_account_info(
                self.secret_data
            )
        )
        self.client = storage.Client(
            project=self.secret_data["project_id"], credentials=self.credentials
        )

    def get_cost_data(self, bucket_name: str):
        _LOGGER.debug(f"[get_cost_data] bucket name: {bucket_name}")

        bucket = self.client.get_bucket(bucket_name)
        blob_names = [blob.name for blob in bucket.list_blobs()]

        for blob_name in blob_names:
            blob = bucket.get_blob(blob_name)

            if blob:
                tmpdir = tempfile.gettempdir()
                csv_file_path = os.path.join(tmpdir, blob_name)
                blob.download_to_filename(csv_file_path)
                costs_data = self._get_csv(csv_file_path)
                _LOGGER.debug(
                    f"[get_cost_data] costs count of {blob_name} : {len(costs_data)}"
                )

                # Paginate
                page_count = int(len(costs_data) / _PAGE_SIZE) + 1

                for page_num in range(page_count):
                    offset = _PAGE_SIZE * page_num
                    yield costs_data[offset : offset + _PAGE_SIZE]

    @staticmethod
    def _check_options(options: dict) -> None:
        if "base_url" not in options or "bucket_name" not in options:
            raise ERROR_REQUIRED_PARAMETER(key="options.base_url")

    @staticmethod
    def _get_csv(csv_file: str) -> List[dict]:
        try:
            df = pd.read_csv(csv_file, encoding="utf-8-sig")
            df = df.replace({np.nan: None})

            costs_data = df.to_dict("records")
            return costs_data

        except Exception as e:
            _LOGGER.error(f"[_get_csv] download error: {e}", exc_info=True)
            raise e
