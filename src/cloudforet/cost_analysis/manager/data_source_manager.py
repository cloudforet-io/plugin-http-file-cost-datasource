import logging

from spaceone.core.manager import BaseManager

from cloudforet.cost_analysis.connector.google_storage_collector import (
    GoogleStorageConnector,
)
from cloudforet.cost_analysis.model.data_source_model import PluginMetadata
from cloudforet.cost_analysis.connector.http_file_connector import HTTPFileConnector

_LOGGER = logging.getLogger(__name__)


class DataSourceManager(BaseManager):
    @staticmethod
    def init_response(options):
        plugin_metadata = PluginMetadata()
        plugin_metadata.validate()
        currency = options.get("currency", "USD")

        if "bucket_name" in options:
            provider = options.get("provider", "google_cloud")
            source = "additional_info.Project ID"
            target = "data.project_id"
            if provider == "aws":
                source = "additional_info.Account ID"
                target = "data.account_id"
            elif provider == "azure":
                source = "additional_info.Subscription Id"
                target = "data.subscription_id"

            return {
                "metadata": {
                    "data_source_rules": [
                        {
                            "name": "match_service_account",
                            "conditions_policy": "ALWAYS",
                            "actions": {
                                "match_service_account": {
                                    "source": source,
                                    "target": target,
                                }
                            },
                            "options": {"stop_processing": True},
                        }
                    ],
                    "currency": currency,
                }
            }

        return {"metadata": plugin_metadata.to_primitive()}

    def verify_plugin(self, options, secret_data, schema):
        if "base_url" in options:
            http_file_connector: HTTPFileConnector = self.locator.get_connector(
                HTTPFileConnector
            )
            http_file_connector.create_session(options, secret_data, schema)
        elif "bucket_name" in options:
            self.locator.get_connector(GoogleStorageConnector, secret_data=secret_data)
