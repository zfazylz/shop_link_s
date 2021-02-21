from saleor.menu.utils import get_merchant_default_nav_menu
from saleor.merchant import models


def resolve_merchant_by_slug(info, slug):
    return models.Merchant.objects.filter(slug=slug).first()


def resolve_merchant_menu(info):
    return get_merchant_default_nav_menu(info.context.user.merchant)
