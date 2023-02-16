from spaceone.core.error import *


class ERROR_EMPTY_BILLED_AT(ERROR_UNKNOWN):
    _message = 'Must have billed_at field or year, month and day fields.: {result}'
