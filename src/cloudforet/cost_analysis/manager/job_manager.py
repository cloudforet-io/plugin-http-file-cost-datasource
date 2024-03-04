import logging
from datetime import datetime, timedelta

from spaceone.core.manager import BaseManager
from cloudforet.cost_analysis.model.job_model import Tasks
from cloudforet.cost_analysis.connector.http_file_connector import HTTPFileConnector

_LOGGER = logging.getLogger(__name__)


class JobManager(BaseManager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.http_file_connector: HTTPFileConnector = self.locator.get_connector(
            HTTPFileConnector
        )

    def get_tasks(self, options, secret_data, schema, start, last_synchronized_at):
        self.http_file_connector.create_session(options, secret_data, schema)

        tasks = []
        changed = []

        for base_url in self.http_file_connector.base_url:
            task_options = {"base_url": base_url}

            tasks.append({"task_options": task_options})
            changed.append({"start": "1900-01"})

        _LOGGER.debug(f"[get_tasks] tasks: {tasks}")
        _LOGGER.debug(f"[get_tasks] changed: {changed}")

        tasks = Tasks({"tasks": tasks, "changed": changed})

        tasks.validate()
        return tasks.to_primitive()
