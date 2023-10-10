from decimal import Decimal
import requests
from celery import shared_task
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
    # TODO uncomment
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


@shared_task(autoretry_for=(Exception,), retry_kwargs={'max_retries': 15, 'countdown': settings.KORAPAY_SECONDS_PER_REQUEST})
def verify_korapay_charge(reference):
    print('verify_korapay_charge')
    from .models import (CustomerTransactionHistory,
                         VendorRiderTransactionHistory)
    headers = {
        'Authorization': f'Bearer {settings.KORAPAY_SECRET_KEY}'
    }
    url = settings.KORAPAY_VERIFY_CHARGE_API + f'/{reference}'
    response = requests.get(url=url, headers=headers)
    print(response.json())
    data = response.json()['data']
    if response.json()['status']:
        if reference.startswith('deposit'):
            try:
                transaction = CustomerTransactionHistory.objects.get(
                    transaction_id=reference.replace('deposit_', ''))
                if transaction.transaction_status == CustomerTransactionHistory.TransactionStatus.PENDING:
                    if data.get('status') == 'success':
                        transaction.title = CustomerTransactionHistory.TransactionTypes.WEB_TOP_UP
                        transaction.transaction_status = CustomerTransactionHistory.TransactionStatus.SUCCESS
                        transaction.save()
                        transaction.customer.wallet += Decimal(data.get('amount'))
                        transaction.customer.save()
                        transaction.customer.notifications.create(
                            title='Deposit Confirmed!',
                            content=f'A deposit of #{transaction.amount} has been added to your wallet balance'
                        )
                    elif data.get('status') in ['expired', 'failed']:
                        transaction.transaction_status = CustomerTransactionHistory.TransactionStatus.FAILED
                        transaction.save()
                        transaction.customer.notifications.create(
                            title='Deposit Failed',
                            content=f'A deposit of #{transaction.amount} has failed'
                        )
                    else:
                        raise Exception
            except CustomerTransactionHistory.DoesNotExist:
                transaction = VendorRiderTransactionHistory.objects.get(
                    transaction_id=data.get('reference').replace('deposit_', ''))
                if transaction.transaction_status == CustomerTransactionHistory.TransactionStatus.PENDING:
                    if data.get('status') == 'success':
                        transaction.title = VendorRiderTransactionHistory.TransactionTypes.WEB_TOP_UP
                        transaction.transaction_status = VendorRiderTransactionHistory.TransactionStatus.SUCCESS
                        transaction.save()
                        transaction.user.wallet += Decimal(data.get('amount'))
                        transaction.user.save()
                        transaction.user.notifications.create(
                            title='Deposit Confirmed!',
                            content=f'A deposit of #{transaction.amount} has been added to your wallet balance'
                        )
                    elif data.get('status') in ['expired', 'failed']:
                        transaction.transaction_status = CustomerTransactionHistory.TransactionStatus.FAILED
                        transaction.save()
                        transaction.customer.notifications.create(
                            title='Deposit Failed',
                            content=f'A deposit of #{transaction.amount} has failed'
                        )
                    else:
                        raise Exception
        else:
            transaction = CustomerTransactionHistory.objects.get(
                transaction_id=data.get('reference').split('_')[-1])
            order = transaction.order
            if data.get('status') == 'success':
                order.is_paid = True
                order.save()
                # vendor_orders = order.vendors.all()
                # print(vendor_orders)
                # for vendor_order in vendor_orders:
                #     vendor_order.vendor.wallet += Decimal(vendor_order.amount)
                #     vendor_order.vendor.save()
                #     vendor_order.vendor.notifications.create(
                #         title='New Order!',
                #         content=f"You have a new order {order}"
                #     )
                order.customer.notifications.create(
                    title='Order Confirmed!',
                    content=f"payment confirmed for {order}"
                )
                transaction.payment_method = order.payment_method
                transaction.save()
            elif data.get('status') in ['expired', 'failed']:
                pass
            else:
                raise Exception
