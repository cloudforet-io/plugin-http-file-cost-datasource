from schematics.models import Model
from schematics.types import ListType, StringType
from schematics.types.compound import ModelType

__all__ = ["Tasks"]


class TaskOptions(Model):
    base_url = StringType(required=True)


class Task(Model):
    task_options = ModelType(TaskOptions, required=True)


class Changed(Model):
    start = StringType(required=True, max_length=7)
    end = StringType(default=None, max_length=7)


class Tasks(Model):
    tasks = ListType(ModelType(Task), required=True)
    changed = ListType(ModelType(Changed), default=[])
