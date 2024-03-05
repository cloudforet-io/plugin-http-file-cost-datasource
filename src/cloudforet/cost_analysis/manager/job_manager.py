import logging

from spaceone.core.error import ERROR_REQUIRED_PARAMETER
from spaceone.core.manager import BaseManager
from cloudforet.cost_analysis.model.job_model import Tasks
from cloudforet.cost_analysis.connector.http_file_connector import HTTPFileConnector

_LOGGER = logging.getLogger(__name__)


class JobManager(BaseManager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_tasks(self, options, secret_data, schema, start, last_synchronized_at):
        tasks = []
        changed = []
        if "base_url" in options:
            http_file_connector = self.locator.get_connector(HTTPFileConnector)
            http_file_connector.create_session(options, secret_data, schema)

            for base_url in http_file_connector.base_url:
                task_options = {"base_url": base_url}

                tasks.append({"task_options": task_options})
                changed.append({"start": "1900-01"})

        elif "bucket_name" in options:
            for bucket_name in options["bucket_name"]:
                task_options = {"bucket_name": bucket_name}

                tasks.append({"task_options": task_options})
                changed.append({"start": "1900-01"})
        else:
            raise ERROR_REQUIRED_PARAMETER(key="options")

        _LOGGER.debug(f"[get_tasks] tasks: {tasks}")
        _LOGGER.debug(f"[get_tasks] changed: {changed}")

        tasks = Tasks({"tasks": tasks, "changed": changed})

        tasks.validate()
        return tasks.to_primitive()
