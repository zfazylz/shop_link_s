import graphene

from saleor.graphql.core.types import Upload
from saleor.graphql.core.types.common import MerchantError
from saleor.graphql.merchant.types import Merchant
from saleor.merchant import models
from saleor.graphql.core.mutations import ModelMutation
from saleor.merchant.thumbnails import create_merchant_thumbnails


class MerchantInput(graphene.InputObjectType):
    title = graphene.String(description="Title", required=True)
    slug = graphene.String(description="Slug for url path", required=True)
    description = graphene.String(description="Description", required=True)
    logo = Upload(description="Logo")


class MerchantUpdateInput(graphene.InputObjectType):
    title = graphene.String(description="Title")
    slug = graphene.String(description="Slug for url path")
    description = graphene.String(description="Description")
    logo = Upload(description="Logo")


class MerchantCreate(ModelMutation):
    class Arguments:
        input = MerchantInput(
            description="Fields required to create a merchant.", required=True
        )

    class Meta:
        description = "Create new merchant"
        exclude = ("owner",)
        model = models.Merchant
        error_type_class = MerchantError
        error_type_field = "merchant_errors"

    @classmethod
    def get_type_for_model(cls):
        return Merchant

    @classmethod
    def post_save_action(cls, info, instance, cleaned_input):
        if 'logo' in cleaned_input:
            create_merchant_thumbnails.delay(instance.pk)

    @classmethod
    def get_instance(cls, info, **data):
        """Get merchant or create mock merchant"""
        instance = getattr(info.context.user, 'merchant', None)
        if instance is None:
            instance = cls._meta.model(owner=info.context.user)
        return instance


class MerchantUpdate(MerchantCreate):
    class Arguments:
        input = MerchantUpdateInput(
            description="Fields required to update a merchant.", required=True
        )

    class Meta:
        description = "Update request user merchant"
        exclude = ("owner",)
        model = models.Merchant
        error_type_class = MerchantError
        error_type_field = "merchant_errors"
