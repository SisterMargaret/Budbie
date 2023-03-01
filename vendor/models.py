from django.db import models

from accounts.models import User, UserProfile
from accounts.utils import send_notification_email, send_verification_email

# Create your models here.
class Vendor(models.Model):
    user = models.OneToOneField(User, related_name="user", on_delete=models.CASCADE)
    user_profile = models.OneToOneField(UserProfile, related_name="userprofile", on_delete=models.CASCADE)
    vendor_name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=100, unique=True)
    vendor_license = models.ImageField(upload_to='vendor/license')
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.vendor_name
    
    def save(self, *args, **kwargs):
        if self.pk is not None:
            #update original
            original_self = Vendor.objects.get(pk = self.pk) 
            if original_self.is_approved != self.is_approved:
                mail_template = "accounts/emails/admin_approval_email.html"
                context = { 'user' : self.user,
                                'is_approved' : self.is_approved
                            }
                if self.is_approved:
                    mail_subject = "Congratulations! your restaurant has been approved"
                    send_notification_email(mail_subject, mail_template, context)
                else:
                    mail_subject = "We are sorry! your restaurant is not eligible to use our platform. Please contact HungryBuff team"
                    send_notification_email(mail_subject, mail_template, context)


        return super(Vendor, self).save(*args, **kwargs)