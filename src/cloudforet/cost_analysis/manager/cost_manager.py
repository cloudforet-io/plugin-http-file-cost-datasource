import logging
from datetime import datetime, timedelta
from dateutil import rrule

from spaceone.core import utils
from spaceone.core.manager import BaseManager
from cloudforet.cost_analysis.error import *
from cloudforet.cost_analysis.connector.http_file_connector import HTTPFileConnector
from cloudforet.cost_analysis.model.cost_model import Cost

_LOGGER = logging.getLogger(__name__)


class CostManager(BaseManager):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.http_file_connector: HTTPFileConnector = self.locator.get_connector(HTTPFileConnector)

    def get_data(self, options, secret_data, schema, task_options):
        self.http_file_connector.create_session(options, secret_data, schema)
        self._check_task_options(task_options)

        base_url = options['base_url']

        response_stream = self.http_file_connector.get_cost_data(base_url)
        for results in response_stream:
            yield self._make_cost_data(results)

    def _make_cost_data(self, results, account_id):
        costs_data = []
        for result in results:
            try:
                data = {
                    'cost': result['usage_cost'],
                    'currency': result['currency'],
                    'usage_quantity': result['usage_quantity'],
                    'provider': result['provider'],
                    'region_code': result['region_code'],
                    'product': result['service_code'],
                    'account': result['account'],
                    'usage_type': self._parse_usage_type(result),
                    'billed_at': datetime.strptime(result['usage_date'], '%Y-%m-%d'),
                    'additional_info': {
                        'raw_usage_type': result.get('usage_type', self._parse_usage_type(result))
                    },
                    'tags': result['usage_type']
                }

            except Exception as e:
                _LOGGER.error(f'[_make_cost_data] make data error: {e}', exc_info=True)
                raise e

            costs_data.append(data)

            # Excluded because schema validation is too slow
            # cost_data = Cost(data)
            # cost_data.validate()
            #
            # costs_data.append(cost_data.to_primitive())

        return costs_data

    @staticmethod
    def _check_task_options(task_options):
        pass

    @staticmethod
    def _parse_usage_type(cost_info):
        service_code = cost_info['service_code']
        usage_type = cost_info['usage_type']

        if service_code == 'AWSDataTransfer':
            if usage_type.find('-In-Bytes') > 0:
                return 'data-transfer.in'
            elif usage_type.find('-Out-Bytes') > 0:
                return 'data-transfer.out'
            else:
                return 'data-transfer.etc'
        elif service_code == 'AmazonCloudFront':
            if usage_type.find('-HTTPS') > 0:
                return 'requests.https'
            elif usage_type.find('-Out-Bytes') > 0:
                return 'data-transfer.out'
            else:
                return 'requests.http'
        else:
            return cost_info['instance_type']
