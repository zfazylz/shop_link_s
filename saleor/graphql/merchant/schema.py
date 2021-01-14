import graphene

from .mutations import (
    MerchantCreate,
)


class MerchantMutations(graphene.ObjectType):
    merchant_create = MerchantCreate.Field()
