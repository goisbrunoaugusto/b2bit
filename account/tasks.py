from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings


@shared_task
def send_follow_notification_email(follower_email, followed_user_email):
    subject = "Você tem um novo seguidor!"
    message = f"Você foi seguido por {follower_email}."
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [followed_user_email],
        fail_silently=False,
    )