import unittest
import time
from unittest.mock import patch

from spaceone.core.unittest.result import print_data
from spaceone.core.unittest.runner import RichTestRunner
from spaceone.core import config
from spaceone.core import utils
from spaceone.core.transaction import Transaction
from cloudforet.cost_analysis.error import *
from cloudforet.cost_analysis.service.data_source_service import DataSourceService
from cloudforet.cost_analysis.connector.http_file_connector import HTTPFileConnector
from test.factory.common_params import *


class TestDataSourceService(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        config.init_conf(package='cloudforet.cost_analysis')
        cls.transaction = Transaction({
            'service': 'cost_analysis',
            'api_class': 'Cost'
        })
        super().setUpClass()

    @classmethod
    def tearDownClass(cls) -> None:
        super().tearDownClass()

    def test_init_data_source(self, *args):
        params = {
            'options': OPTIONS,
            'secret_data': SECRET_DATA
        }

        self.transaction.method = 'init'
        data_source_svc = DataSourceService(transaction=self.transaction)
        response = data_source_svc.init(params.copy())
        print_data(response, 'test_init_data_source')

    @patch.object(HTTPFileConnector, '__init__', return_value=None)
    @patch.object(HTTPFileConnector, 'create_session', return_value=None)
    def test_verify_data_source(self, *args):
        params = {
            'options': OPTIONS,
            'secret_data': SECRET_DATA
        }

        self.transaction.method = 'verify'
        data_source_svc = DataSourceService(transaction=self.transaction)
        data_source_svc.verify(params.copy())


if __name__ == "__main__":
    unittest.main(testRunner=RichTestRunner)
