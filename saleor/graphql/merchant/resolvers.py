from saleor.merchant import models


def resolve_merchant_by_slug(info, slug):
    return models.Merchant.objects.filter(slug=slug).first()
