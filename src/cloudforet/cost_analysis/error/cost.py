from spaceone.core.error import *


class ERROR_INVALID_COLUMN(ERROR_UNKNOWN):
    _message = 'Invalid column: {column}'


class ERROR_INVALID_BILLED_AT(ERROR_UNKNOWN):
    _message = 'Invalid billed_at: {billed_at}, check the type of billed_at'
