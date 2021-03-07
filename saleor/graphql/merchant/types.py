import graphene
from graphene_django import DjangoObjectType

from .resolvers import resolve_featured_products
from ..core.fields import PrefetchingConnectionField
from ..core.types import Image
from ..menu.types import Menu
from ..product.types import Product
from ...menu.utils import get_merchant_default_nav_menu
from ...merchant import models


class Merchant(DjangoObjectType):
    menu = graphene.Field(type=Menu)
    featured_products = PrefetchingConnectionField(Product)
    logo = graphene.Field(type=graphene.String, source='get_logo_or_default')
    thumbnail = graphene.Field(
        Image,
        description="The main thumbnail for a product.",
        size=graphene.Argument(graphene.Int, description="Size of thumbnail."),
    )

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
        return resolve_featured_products(root, info)

    @staticmethod
    def resolve_thumbnail(root: models.Merchant, info, size=100, **_kwargs):
        if root.logo:
            return Image.get_adjusted(
                image=root.logo,
                alt=root.title,
                size=size,
                rendition_key_set="merchant_logos",
                info=info,
            )
        else:
            url = info.context.build_absolute_uri(root.logo_placeholder)
            return Image(url, root.title)

