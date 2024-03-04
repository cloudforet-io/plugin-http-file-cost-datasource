from spaceone.core.error import *


class ERROR_EMPTY_BILLED_DATE(ERROR_UNKNOWN):
    _message = "Must have billed_date field or year, month fields.: {result}"
