import string
from datetime import timedelta
from random import choices as random_choices

from django.conf import settings
from django.db import models
from django.utils import timezone

from saleor.account.models import PossiblePhoneNumberField


def _generate_sms_code():
    if settings.DEBUG:
        return settings.DEFAULT_SMS_CODE
    return ''.join(random_choices(string.digits, k=6))


class SMSCode(models.Model):
    phone = PossiblePhoneNumberField()
    code = models.CharField(max_length=6, default=_generate_sms_code)
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-created_at',)

    def is_valid(self):
        expires = self.created_at - timedelta(seconds=settings.SMS_CODE_EXPIRE)
        if not self.is_used and expires < timezone.now():
            return True
        return False
