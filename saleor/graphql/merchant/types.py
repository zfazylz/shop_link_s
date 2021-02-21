import graphene
from graphene_django import DjangoObjectType

from .resolvers import resolve_merchant_menu
from ..menu.types import Menu
from ...merchant import models


class Merchant(DjangoObjectType):
    menu = graphene.Field(type=Menu)

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
        return resolve_merchant_menu(info)
