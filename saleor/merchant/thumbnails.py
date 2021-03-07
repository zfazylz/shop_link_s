from ..celeryconf import app
from ..core.utils import create_thumbnails
from .models import Merchant


@app.task
def create_merchant_thumbnails(merchant_id: str):
    """Take a Merchant model and create thumbnails for it."""
    create_thumbnails(
        pk=merchant_id,
        model=Merchant,
        size_set="merchant_logos",
        image_attr="logo",
    )
