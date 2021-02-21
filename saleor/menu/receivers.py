from django.db.models.signals import post_save
from django.dispatch import receiver

from saleor.menu.utils import update_default_menu
from saleor.product.models import Product


@receiver(post_save, sender=Product)
def update_default_menu_receiver(instance, **kwargs):
    update_default_menu(instance.merchant)
