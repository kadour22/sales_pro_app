from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Profile
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings

@receiver(post_save , sender=User)
def create_user_account(sender, instance, created, **kwargs) :
    if created :
        account = Profile.objects.create(user=instance)

        account.save()
