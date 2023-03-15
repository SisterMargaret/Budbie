from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from accounts.models import User, UserProfile
#Signals
@receiver(post_save, sender=User)
def post_save_user_create_profile_receiver(sender, instance, created, **kwargs):
    
    if created:
        UserProfile.objects.create(user=instance)
    else:
        try:
            profile = UserProfile.objects.get(user=instance)
            profile.save()
        except:
            UserProfile.objects.create(user=instance)

@receiver(pre_save, sender=User)
def pre_save_user(sender, instance, **kwargs):
    print('Pre save fired')