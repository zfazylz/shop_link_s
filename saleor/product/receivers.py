from django.db.models.signals import post_save
from django.dispatch import receiver

from saleor.product.models import Product, MerchantVisibleCategory


@receiver(post_save, sender=Product)
def update_category_cache_data(instance: "Product", **kwargs):
    if not any((instance.visible_in_listings, instance.is_visible, instance.variants.exists())):
        return

    obj, is_created = MerchantVisibleCategory.objects.get_or_create(
        category=instance.category, merchant=instance.merchant
    )

    if is_created:
        categories_to_create = []
        for category in instance.category.get_ancestors():
            categories_to_create.append(
                MerchantVisibleCategory(
                    merchant=instance.merchant, category=category
                )
            )
        MerchantVisibleCategory.objects.bulk_create(categories_to_create, ignore_conflicts=True)
