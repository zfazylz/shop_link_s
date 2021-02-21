from django.conf import settings
from django.db import models
from versatileimagefield.fields import VersatileImageField


class Merchant(models.Model):
    owner = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        related_name="merchant",
        on_delete=models.CASCADE,
    )
    title = models.CharField(max_length=250)
    slug = models.SlugField(unique=True, null=True, blank=True)
    description = models.TextField(max_length=1000)
    logo = VersatileImageField(upload_to="merchant-logos")

    class Meta:
        ordering = ("-id",)

    def __str__(self):
        return f"Merchant <{self.slug} ({self.title})>"
