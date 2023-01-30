import unittest
import os
from datetime import datetime, timedelta
from unittest.mock import patch

from spaceone.core.unittest.result import print_data
from spaceone.core.unittest.runner import RichTestRunner
from spaceone.core import config
from spaceone.core import utils
from spaceone.core.transaction import Transaction
from cloudforet.cost_analysis.manager.cost_manager import CostManager
from cloudforet.cost_analysis.connector.http_file_connector import HTTPFileConnector


class TestHTTPFileConnector(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        config.init_conf(package='spaceone.cost_analysis')
        config_path = os.environ.get('TEST_CONFIG')
        test_config = utils.load_yaml_from_file(config_path)

        cls.secret_data = test_config.get('secret_data', {})
        cls.options = test_config.get('options', {})
        cls.schema = None
        cls.task_options = None

        cls.http_file_connector = HTTPFileConnector(Transaction(), {})
        super().setUpClass()

    @classmethod
    def tearDownClass(cls) -> None:
        super().tearDownClass()

    def test_create_session(self):
        self.http_file_connector.create_session(self.options, self.secret_data)

    def test_list_metrics(self):
        cost_mgr = CostManager()
        responses = cost_mgr.get_data(self.options, self.secret_data, self.schema, self.task_options)
        # self.aws_credentials['region_name'] = self.resource.get('region_name')
        #
        # self.aws_connector.create_session(self.schema, {}, self.aws_credentials)
        # metrics_info = self.aws_connector.list_metrics(namespace, dimensions)
        #
        # print_data(metrics_info, 'test_list_metrics')


if __name__ == "__main__":
    unittest.main(testRunner=RichTestRunner)
