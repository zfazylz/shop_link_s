from saleor.graphql.utils import get_user_or_app_from_context
from saleor.merchant import models
from saleor.product import models as product_models


def resolve_merchant_by_slug(info, slug):
    return models.Merchant.objects.filter(slug=slug).first()


def resolve_featured_products(merchant: models.Merchant, info):
    requestor = get_user_or_app_from_context(info.context)
    return product_models.Product.objects.for_merchant(merchant) \
        .visible_to_user(requestor)
