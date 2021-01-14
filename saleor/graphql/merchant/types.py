import graphene
from graphene_django import DjangoObjectType

from ...merchant import models


class Merchant(DjangoObjectType):
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
        ]
