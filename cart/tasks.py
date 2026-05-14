from celery import shared_task
import time
from django.core.mail import send_mail
from django.conf import settings

@shared_task
def send_email_task(email):

    print("Sending email...")

    time.sleep(2)
    send_mail(
        subject="From celery worker",
        message="This email is sended with using django background task and celorn worker!",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[
            "mail.achibhossen@gmail.com",
            "dev.achibhossen@gmail.com",
        ]
    )

    print(f"Email sent to {email}")