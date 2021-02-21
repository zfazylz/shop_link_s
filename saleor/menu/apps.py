from django.apps import AppConfig


class MenuConfig(AppConfig):
    name = 'saleor.menu'

    def ready(self):
        from . import receivers
