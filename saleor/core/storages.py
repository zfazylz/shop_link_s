import os

import cloudinary.uploader
from cloudinary_storage.storage import MediaCloudinaryStorage
from django.conf import settings
from storages.backends.gcloud import GoogleCloudStorage
from storages.backends.s3boto3 import S3Boto3Storage


class S3MediaStorage(S3Boto3Storage):
    def __init__(self, *args, **kwargs):
        self.bucket_name = settings.AWS_MEDIA_BUCKET_NAME
        self.custom_domain = settings.AWS_MEDIA_CUSTOM_DOMAIN
        super().__init__(*args, **kwargs)


class GCSMediaStorage(GoogleCloudStorage):
    def __init__(self, *args, **kwargs):
        self.bucket_name = settings.GS_MEDIA_BUCKET_NAME
        super().__init__(*args, **kwargs)


class CustomMediaCloudinaryStorage(MediaCloudinaryStorage):
    def _upload(self, name, content):
        options = {'use_filename': True, 'resource_type': self._get_resource_type(name), 'tags': self.TAG}
        folder = os.path.dirname(name)
        if folder:
            options['folder'] = folder
        options['unique_filename'] = False
        return cloudinary.uploader.upload(content, **options)
