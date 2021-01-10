import graphene
from django.core.exceptions import ValidationError

from saleor.account.validators import validate_possible_number
from saleor.graphql.core.mutations import ModelMutation
from saleor.graphql.core.types.common import SMSError
from saleor.graphql.sms.types import SMSCode
from saleor.sms import models


class PhoneNumberInput(graphene.InputObjectType):
    phone = graphene.String(description="The phone number", required=True)


class SendSMS(ModelMutation):
    class Arguments:
        input = PhoneNumberInput()

    class Meta:
        description = "Send random SMS code to phone"
        model = models.SMSCode
        error_type_class = SMSError
        error_type_field = "sms_errors"

    @classmethod
    def clean_input(cls, info, instance, data, input_cls=None):
        try:
            validate_possible_number(data["phone"])
        except ValidationError as e:
            raise ValidationError(({"phone": e}))
        return data

    @classmethod
    def get_type_for_model(cls):
        return SMSCode
