from django.apps import AppConfig


class ProductConfig(AppConfig):
    name = 'saleor.product'

    def ready(self):
        from . import receivers
