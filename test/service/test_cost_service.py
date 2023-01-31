import unittest
from datetime import datetime, timedelta
from unittest.mock import patch

from spaceone.core.unittest.result import print_data
from spaceone.core.unittest.runner import RichTestRunner
from spaceone.core import config
from spaceone.core import utils
from spaceone.core.transaction import Transaction

from cloudforet.cost_analysis.connector.http_file_connector import HTTPFileConnector
from cloudforet.cost_analysis.service.cost_service import CostService
from cloudforet.cost_analysis.info.cost_info import CostInfo, CostsInfo
from test.factory.common_params import *


class TestCostService(unittest.TestCase):

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

    @patch.object(HTTPFileConnector, '__init__', return_value=None)
    def test_get_cost_data(self, *args):
        params = {
            'options': OPTIONS,
            'secret_data': {},
            'task_options': {}
        }

        self.transaction.method = 'get_data'
        cost_svc = CostService(transaction=self.transaction)
        responses = cost_svc.get_data(params.copy())

        for response in responses:
            print_data(response, 'test_get_cost_data')


if __name__ == "__main__":
    unittest.main(testRunner=RichTestRunner)
