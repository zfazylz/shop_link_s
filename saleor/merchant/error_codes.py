from enum import Enum


class MerchantErrorCode(Enum):
    INVALID = "invalid"
    GRAPHQL_ERROR = "graphql_error"
    NOT_FOUND = "not_found"
    REQUIRED = "required"
    UNIQUE = "unique"
