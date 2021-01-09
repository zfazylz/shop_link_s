from saleor.sms.models import SMSCode


def send_sms_code(phone: str):
    SMSCode.objects.create(phone)


def verify_sms_code(phone: str, code: str):
    """
    One time sms code verification
    """
    sms = SMSCode.objects.filter(phone=phone).first()
    if sms and sms.is_valid() and sms.code == code:
        sms.is_used = True
        sms.save()
        return True
    return False
