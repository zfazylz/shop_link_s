import graphene
from graphene_django import DjangoObjectType

from ...sms import models


class SMSCode(DjangoObjectType):
    phone = graphene.String(description="Phone number.")

    class Meta:
        description = "Represents user address data."
        interfaces = [graphene.relay.Node]
        model = models.SMSCode
        only_fields = ["phone", ]
