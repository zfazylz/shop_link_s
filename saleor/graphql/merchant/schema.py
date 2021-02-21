import graphene

from .mutations import (
    MerchantCreate,
)
from .resolvers import resolve_merchant_by_slug, resolve_merchant_menu
from .types import Merchant
from ..core.fields import FilterInputConnectionField
from ..core.validators import validate_one_of_args_is_in_query
from ..menu.types import Menu


class MerchantQueries(graphene.ObjectType):
    merchants = FilterInputConnectionField(
        Merchant,
        description="List of the registered merchants.",
    )
    merchant = graphene.Field(
        Merchant,
        id=graphene.Argument(graphene.ID, description="ID of the merchant.", ),
        slug=graphene.Argument(graphene.String, description="Slug of the merchant"),
        description="Look up a merchant by ID or Slug",
    )

    def resolve_merchant(self, info, id=None, slug=None):
        validate_one_of_args_is_in_query("id", id, "slug", slug)
        if id:
            return graphene.Node.get_node_from_global_id(info, id, Merchant)
        if slug:
            return resolve_merchant_by_slug(info, slug=slug)


class MerchantMutations(graphene.ObjectType):
    merchant_create = MerchantCreate.Field()
