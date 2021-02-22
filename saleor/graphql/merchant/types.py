import graphene
from graphene_django import DjangoObjectType

from .resolvers import resolve_featured_products
from ..core.fields import PrefetchingConnectionField
from ..menu.types import Menu
from ..product.types import Product
from ...menu.utils import get_merchant_default_nav_menu
from ...merchant import models


class Merchant(DjangoObjectType):
    menu = graphene.Field(type=Menu)
    featured_products = PrefetchingConnectionField(Product)

    class Meta:
        description = "Represents a Merchant."
        interfaces = [graphene.relay.Node]
        model = models.Merchant
        only_fields = [
            "owner",
            "title",
            "slug",
            "description",
            "logo",
            "menu"
        ]

    def resolve_menu(self, info):
        return get_merchant_default_nav_menu(self)

    @staticmethod
    def resolve_featured_products(root: models.Merchant, info, **_kwargs):
        return resolve_featured_products(root)
