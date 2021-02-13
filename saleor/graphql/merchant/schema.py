import graphene

from .mutations import (
    MerchantCreate,
)
from .types import Merchant
from ..core.fields import FilterInputConnectionField


class MerchantQueries(graphene.ObjectType):
    merchants = FilterInputConnectionField(
        Merchant,
        description="List of the registered merchants.",
    )


class MerchantMutations(graphene.ObjectType):
    merchant_create = MerchantCreate.Field()
