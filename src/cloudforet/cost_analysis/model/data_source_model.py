from schematics.models import Model
from schematics.types import ListType, DictType, StringType, IntType, BooleanType
from schematics.types.compound import ModelType

__all__ = ["PluginMetadata"]


class MatchServiceAccount(Model):
    source = StringType(required=True)
    target = StringType(required=True)


class Actions(Model):
    match_service_account = ModelType(MatchServiceAccount)


class Options(Model):
    stop_processing = BooleanType(default=False)


class Condition(Model):
    key = StringType(required=True)
    value = StringType(required=True)
    operator = StringType(
        required=True, choices=["eq", "contain", "not", "not_contain"]
    )


class DataSourceRule(Model):
    name = StringType(required=True)
    conditions = ListType(ModelType(Condition), default=[])
    conditions_policy = StringType(required=True, choices=["ALL", "ANY", "ALWAYS"])
    actions = ModelType(Actions, required=True)
    options = ModelType(Options, default={})
    tags = DictType(StringType, default={})


class PluginMetadata(Model):
    data_source_rules = ListType(ModelType(DataSourceRule), default=[])
    currency = StringType(required=True, default="USD")
