import graphene

from saleor.graphql.core.types import Upload
from saleor.graphql.core.types.common import MerchantError
from saleor.graphql.merchant.types import Merchant
from saleor.merchant import models
from saleor.graphql.core.mutations import ModelMutation


class MerchantInput(graphene.InputObjectType):
    title = graphene.String(description="Title", required=True)
    slug = graphene.String(description="Slug for url path", required=True)
    description = graphene.String(description="Description", required=True)
    logo = Upload(description="Logo", required=True)


class MerchantCreate(ModelMutation):
    class Arguments:
        input = MerchantInput(
            description="Fields required to create a merchant.", required=True
        )

    class Meta:
        description = "Create new merchant"
        exclude = ["owner"]
        model = models.Merchant
        error_type_class = MerchantError
        error_type_field = "merchant_errors"

    @classmethod
    def perform_mutation(cls, root, info, **data):
        return super().perform_mutation(root, info, **data)

    @classmethod
    def clean_input(cls, info, instance, data, input_cls=None):
        instance.owner = info.context.user
        return super().clean_input(info, instance, data, input_cls)

    @classmethod
    def get_type_for_model(cls):
        return Merchant
