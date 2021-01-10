from enum import Enum


class SMSErrorCode(str, Enum):
    GRAPHQL_ERROR = "graphql_error"
    INVALID = "invalid"
