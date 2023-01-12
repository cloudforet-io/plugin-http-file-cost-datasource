import logging

from spaceone.core.manager import BaseManager
from cloudforet.cost_analysis.model.data_source_model import PluginMetadata
from cloudforet.cost_analysis.connector.spaceone_connector import SpaceONEConnector

_LOGGER = logging.getLogger(__name__)


class DataSourceManager(BaseManager):

    @staticmethod
    def init_response(options):
        plugin_metadata = PluginMetadata()
        plugin_metadata.validate()

        return {
            'metadata': plugin_metadata.to_primitive()
        }

    def verify_plugin(self, options, secret_data, schema):
        space_connector: SpaceONEConnector = self.locator.get_connector('SpaceONEConnector')
        space_connector.init_client(options, secret_data, schema)
        space_connector.verify_plugin()

        # aws_s3_connector: AWSS3Connector = self.locator.get_connector('AWSS3Connector')
        # aws_s3_connector.create_session(options, secret_data, schema)
