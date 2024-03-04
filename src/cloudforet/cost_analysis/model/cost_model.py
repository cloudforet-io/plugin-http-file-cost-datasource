from schematics.models import Model
from schematics.types import DictType, StringType, FloatType, DateTimeType

__all__ = ["Cost"]


class Cost(Model):
    cost = FloatType(required=True)
    usage_quantity = FloatType(required=True)
    usage_type = StringType()
    usage_unit = StringType(default=None)
    provider = StringType(required=True)
    region_code = StringType()
    product = StringType()
    resource = StringType()
    billed_date = StringType(required=True, max_length=7)
    additional_info = DictType(StringType, default={})
    tags = DictType(StringType, default={})
