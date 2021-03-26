from django.db.models import Count, Q

from saleor.menu.models import Menu, MenuItem
from saleor.merchant.models import Merchant
from saleor.product.models import Category


def _get_default_category_menu_slug(merchant: Merchant):
    return 'default-category-menu-merchant-' + str(merchant.id)


def update_default_menu(merchant: Merchant):
    """
    TODO: Fix this
    """
    menu, _ = Menu.objects.get_or_create(
        merchant=merchant,
        # TODO: restrict such slugs for merchant on create
        slug=_get_default_category_menu_slug(merchant),
        defaults={'name': 'Меню категории'}
    )
    categories = Category.objects.filter(
        products__merchant=merchant
    ).annotate(
        product_count=Count('products', filter=Q(products__merchant=merchant))
    ).order_by('-product_count')
    total_categories = categories.count()
    menu_item_length = _max_categories = 3
    do_create_extra_menu_item = total_categories > 3
    if do_create_extra_menu_item:
        menu_item_length = _max_categories - 1
    for category in categories[:menu_item_length]:
        MenuItem.objects.update_or_create(
            menu=menu,
            parent=None,
            category=category,
            defaults={'name': category.name},
        )
    if do_create_extra_menu_item:
        all_categories_menu, _ = MenuItem.objects.get_or_create(
            menu=menu,
            category=None,
            collection=None,
            page=None,
            parent=None,
            url=f'/{merchant.slug}/',
            defaults={'name': 'Все категории'}
        )
        for category in categories:
            MenuItem.objects.update_or_create(
                menu=menu,
                parent=all_categories_menu,
                category=category,
                name=category.name,
            )


def get_merchant_default_nav_menu(merchant: Merchant):
    menu = Menu.objects.filter(
        merchant=merchant, slug=_get_default_category_menu_slug(merchant)
    ).first()
    return menu
