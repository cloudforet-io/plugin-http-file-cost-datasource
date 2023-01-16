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
            'options': {
                'base_url': 'https://cloudforet.io/',
                'columns_header': {
                    'resource_cost': 'cost',
                    'currency': 'currency',
                    'usage_quantity': 'usage_quantity',
                    'infra_type': '',
                    'product_region': '',
                    'category_name': '',
                    'sub_category_name': '',
                    'product_service_code': '',
                    'account_id': '',
                    'usage_type': '',
                    'usage_date': ''
                }
            },
            'secret_data': {'auth_type': 'basic',
                            'auth_options': {'username': 'seolmin',
                                             'password': '1234'}},
            'task_options': {}
        }

        self.transaction.method = 'get_data'
        cost_svc = CostService(transaction=self.transaction)
        response = cost_svc.get_data(params.copy())
        print_data(response, 'test_get_cost_data')


if __name__ == "__main__":
    unittest.main(testRunner=RichTestRunner)
