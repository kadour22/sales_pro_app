from celery import shared_task
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings

@shared_task
def send_upload_notification(email, filename):
    subject = 'Your file was uploaded'
    message = f'Hello!\n\nYour file "{filename}" has been successfully uploaded and is being analyzed.'
    print("Done.. 😍")
    send_mail(subject, message, settings.EMAIL_HOST_USER,recipient_list=[email])