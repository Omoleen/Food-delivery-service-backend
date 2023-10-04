from celery import shared_task
import requests
from django.conf import settings


@shared_task
def delete_unverified_user(phone_number):
    print('delete_unverified_user')
    from .models import VerifyPhone
    phone = VerifyPhone.objects.get(phone_number=phone_number)
    if not phone.is_verified:
        phone.delete()


@shared_task
def change_code(phone_number, otp):
    print('change_code')
    from .models import VerifyPhone
    try:
        phone = VerifyPhone.objects.get(phone_number=phone_number, otp=otp)
        phone.generate_code(False)
        phone.save()
    except VerifyPhone.DoesNotExist:
        pass


@shared_task
def send_otp_sms(phone_number, otp, created):
    print('send_otp_sms')
    url = "https://termii.com/api/sms/send"
    payload = {
        "to": f"{phone_number}",
        "from": "Eatup",
        "sms": f"{otp} is your EatUp OTP code. code is active for 10 minutes only, one time use",
        "type": "plain",
        "channel": "generic",
        "api_key": settings.TERMII_API_KEY,
    }
    headers = {
        'Content-Type': 'application/json',
    }
    response = requests.request("POST", url, headers=headers, json=payload)
    # print(response)
    print(response.json())
    # if created:
    #     delete_unverified_user.apply_async([phone_number], countdown=1800)
    return response.ok


@shared_task
def send_push_message(body='Hello World!', title='EatUp', token='ExponentPushToken[sNBH5AONBc4S8Uw7RLSSFZ]', extra=None):
    headers = {
        # "Authorization": f"Bearer {os.getenv('EXPO_TOKEN')}",
        'host': 'exp.host',
        "accept": "application/json",
        "accept-encoding": "gzip, deflate",
        "content-type": "application/json",
    }
    data = {
        'to': token,
        'title': title,
        'body': body,
        'priority': 'high'
        # 'data': {}
    }

    response = requests.post(url='https://exp.host/--/api/v2/push/send', headers=headers, json=data)
    print(response.json())