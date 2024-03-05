import logging
from dateutil.parser import parse
from spaceone.core.manager import BaseManager
from cloudforet.cost_analysis.error import *
from cloudforet.cost_analysis.connector.http_file_connector import HTTPFileConnector
from cloudforet.cost_analysis.connector.google_storage_collector import (
    GoogleStorageConnector,
)

_LOGGER = logging.getLogger(__name__)

_REQUIRED_FIELDS = ["cost", "currency", "billed_date"]


class CostManager(BaseManager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.default_vars = None
        self.field_mapper = None

    def get_data(self, options, secret_data, schema, task_options):
        self._check_task_options(task_options)

        if "default_vars" in options:
            self.default_vars = options["default_vars"]

        if "field_mapper" in options:
            self.field_mapper = options["field_mapper"]

        if "base_url" in task_options:
            base_url = task_options["base_url"]
            http_file_connector = self.locator.get_connector(HTTPFileConnector)
            http_file_connector.create_session(options, secret_data, schema)
            response_stream = http_file_connector.get_cost_data(base_url)
        else:
            # just for Google Cloud Storage
            bucket_name = task_options["bucket_name"]
            storage_connector = self.locator.get_connector(
                GoogleStorageConnector, secret_data=secret_data
            )
            response_stream = storage_connector.get_cost_data(bucket_name)

        for results in response_stream:
            yield self._make_cost_data(results)

    def _make_cost_data(self, results):
        costs_data = []
        for result in results:
            result = self._apply_strip_to_dict_keys(result)
            result = self._apply_strip_to_dict_values(result)

            if self.default_vars:
                result = self._change_result_by_field_mapper(result)

            if self.field_mapper:
                self._set_default_vars(result)

            self._create_billed_date(result)

            if not self._convert_cost_and_usage_quantity_types(result):
                continue

            if not self._exist_cost_and_usage_quantity(result):
                continue

            self._check_required_fields(result)

            try:
                data = {
                    "cost": result["cost"],
                    "usage_quantity": result.get("usage_quantity", 0),
                    "usage_type": result.get("usage_type"),
                    "usage_unit": result.get("usage_unit"),
                    "provider": result.get("provider"),
                    "region_code": result.get("region_code"),
                    "product": result.get("product"),
                    "resource": result.get("resource", ""),
                    "billed_date": result["billed_date"],
                    "additional_info": result.get("additional_info", {}),
                    "tags": result.get("tags", {}),
                }

            except Exception as e:
                _LOGGER.error(f"[_make_cost_data] make data error: {e}", exc_info=True)
                raise e

            costs_data.append(data)
        return costs_data

    @staticmethod
    def _check_task_options(task_options):
        if "base_url" not in task_options or "bucket_name" not in task_options:
            raise ERROR_REQUIRED_PARAMETER(key="task_options")

    @staticmethod
    def _apply_strip_to_dict_keys(result):
        for key in list(result.keys()):
            new_key = key.strip()
            if new_key != key:
                result[new_key] = result[key]
                del result[key]
        return result

    @staticmethod
    def _apply_strip_to_dict_values(result):
        for key, value in result.items():
            if isinstance(value, str):
                result[key] = value.strip()
        return result

    def _change_result_by_field_mapper(self, result):
        for origin_field, actual_field in self.field_mapper.items():
            if isinstance(actual_field, str):
                if actual_field in result:
                    result[origin_field] = result[actual_field]
                    del result[actual_field]

            if origin_field == "additional_info":
                additional_info = {}
                for (
                    origin_additional_field,
                    actual_additional_field,
                ) in actual_field.items():
                    additional_info[origin_additional_field] = result[
                        actual_additional_field
                    ]
                    del result[actual_additional_field]
                result[origin_field] = additional_info

        return result

    def _create_billed_date(self, result):
        if self._exist_billed_date(result):
            billed_date = result["billed_date"]
            billed_date = self._apply_parse_date(billed_date)
            billed_date = str(billed_date.strftime("%Y-%m-%d"))

            result["billed_date"] = billed_date

        else:
            year = result["year"]
            month = result["month"]
            day = result.get("day", "01")

            if len(month) == 1:
                month = f"0{month}"
            if len(day) == 1:
                day = f"0{day}"

            billed_date = f"{year}-{month}-{day}"

            result["billed_date"] = billed_date

        return result

    @staticmethod
    def _exist_billed_date(result):
        if result.get("billed_date"):
            return True
        elif result.get("year") and result.get("month"):
            return False
        else:
            _LOGGER.error(f"[_is_not_empty_billed_at] billed_at is empty: {result}")
            raise ERROR_EMPTY_BILLED_DATE(result=result)

    @staticmethod
    def _apply_parse_date(date):
        try:
            parsed_date = parse(date)
            return parsed_date
        except TypeError as e:
            _LOGGER.error(f"[_apply_parse_date] parse date error: {e}", exc_info=True)
            raise e

    def _set_default_vars(self, result):
        for key, value in self.default_vars.items():
            result[key] = value

    @staticmethod
    def _convert_cost_and_usage_quantity_types(result):
        try:
            result["cost"] = float(result["cost"])
            result["usage_quantity"] = float(result.get("usage_quantity", 0))
        except Exception as e:
            _LOGGER.error(
                f"[_convert_cost_and_usage_quantity_types] convert cost and usage quantity types error: {e} (data={result})",
                exc_info=True,
            )
            return False
        return True

    @staticmethod
    def _exist_cost_and_usage_quantity(result):
        if result["cost"] or result["cost"] == float(0):
            return True
        elif result["usage_quantity"] or result["usage_quantity"] == float(0):
            return True
        else:
            _LOGGER.error(
                f"[_exist_cost_and_usage_quantity] cost or usage quantity are empty: {result}"
            )
            return False

    @staticmethod
    def _check_required_fields(result):
        for field in _REQUIRED_FIELDS:
            if field not in result:
                raise ERROR_REQUIRED_PARAMETER(key=field)
