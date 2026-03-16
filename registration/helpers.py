import random
from datetime import timedelta, datetime

import requests
from django.core.mail import send_mail
from django.db.models import Q
from django.template.loader import render_to_string
from django.utils import timezone

from .models import ManageOtp, EmailTracking


def generate_otp_and_send_email(user, module_name):
    # Delete All codes before create and send the new one
    ManageOtp.objects.filter(user_id=user).delete()

    # Generate OTP
    otp = random.randint(100000, 999999)

    # Create new otp object for current user
    ManageOtp.objects.create(
        otp_code=otp,
        user=user
    )

    # Send email with otp
    subject = "Email verification OTP"
    recipient_list = [user.email]
    content = render_to_string('otp_email.html', {
        'first_name': user.first_name,
        'otp': otp
    })
    res = send_mail(
        subject=subject, message='', from_email=None, recipient_list=recipient_list, fail_silently=True, html_message=content
    )
    EmailTracking.objects.create(module_name=module_name, user=user) if res == 1 else None

    return res


def send_password_reset_email(user, reset_link, module_name):
    # Send email with otp
    subject = "Password Reset"
    content = render_to_string('password_reset_email.html', {
        'first_name': user.first_name,
        'url': reset_link
    })
    recipient_list = [user.email]
    res = send_mail(
        subject=subject, message='', from_email=None, recipient_list=recipient_list, fail_silently=True, html_message=content
    )
    EmailTracking.objects.create(module_name=module_name, user=user) if res == 1 else None

    return res


def check_google_auth_token(token):
    url = "https://www.googleapis.com/oauth2/v2/tokeninfo?access_token={0}".format(token)
    social_verification = requests.get(url)
    return social_verification.status_code == 200


def track_email(user, module_name, seconds):
    email_tracking_obj = EmailTracking.objects.filter(
        Q(user_id=user) & Q(module_name=module_name) & Q(status=1)).first()
    if email_tracking_obj:
        sent_at = timezone.make_naive(email_tracking_obj.sent_at)
        # print(datetime.now().second - (sent_at + timedelta(seconds=seconds)).second)
        # print((sent_at + timedelta(seconds=seconds)).second - datetime.now().second)
        # print(seconds)
        # remaining_seconds = seconds - (sent_at + timedelta(seconds=seconds)).second
        # message = {'resend': f'Please retry after {remaining_seconds} seconds'}
        if not (sent_at + timedelta(seconds=seconds) < datetime.now()):
            return False
        else:
            email_tracking_obj.status = 2
            email_tracking_obj.save()
            return True
    else:
        return None
