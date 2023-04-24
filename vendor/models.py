from datetime import date, datetime, time
from django.db import models

from accounts.models import User, UserProfile
from accounts.utils import send_notification_email, send_verification_email
from foodapp_main import settings
import stripe
# Create your models here.
class Vendor(models.Model):
    user = models.OneToOneField(User, related_name="user", on_delete=models.CASCADE)
    user_profile = models.OneToOneField(UserProfile, related_name="userprofile", on_delete=models.CASCADE)
    vendor_name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=100, unique=True)
    vendor_license = models.ImageField(upload_to='vendor/license')
    vat_number=models.CharField(max_length=12, null=True, blank=True)
    is_approved = models.BooleanField(default=False)
    is_payment_account_setup = models.BooleanField(default=False, null=True)
    payment_account_key = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.vendor_name
    
    def is_open(self):
        today = date.today().isoweekday()
        current_day_hours = OpeningHour.objects.filter(vendor=self, day=today)
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        is_open = None
        for i in current_day_hours:
            if i.is_closed:
                is_open = False
            else:
                start = str(datetime.strptime(i.from_hour, "%I:%M %p").time())
                end = str(datetime.strptime(i.to_hour, "%I:%M %p").time())
                
                if current_time > start and current_time < end:
                    is_open =True
                    break
                else:
                    is_open = False
        return is_open
    
    def save(self, *args, **kwargs):
        if self.pk is not None:
            #update original
            original_self = Vendor.objects.get(pk = self.pk) 
            if original_self.is_approved != self.is_approved:
                mail_template = "accounts/emails/admin_approval_email.html"
                context = { 'user' : self.user,
                            'is_approved' : self.is_approved,
                            'to_email' : self.user.email
                        }
                if self.is_approved:
                    mail_subject = "Congratulations! your restaurant has been approved"
                    send_notification_email(mail_subject, mail_template, context)
                else:
                    mail_subject = "We are sorry! your restaurant is not eligible to use our platform. Please contact HungryBuff team"
                    send_notification_email(mail_subject, mail_template, context)


        return super(Vendor, self).save(*args, **kwargs)
    
    def is_stripe_setup_complete(self):
        if not self.is_payment_account_setup :
            if self.payment_account_key:
                stripe.api_key = settings.STRIPE_SECRET_KEY
                account = stripe.Account.retrieve(id=self.payment_account_key)
                if account.details_submitted and account.charges_enabled:
                    return True
        return False
        
DAYS= [
    (1, ("Monday")),
    (2, ("Tuesday")),
    (3, ("Wednesday")),
    (4, ("Thursday")),
    (5, ("Friday")),
    (6, ("Saturday")),
    (7, ("Sunday")),
]    

HOURS_OF_DAY_24 =  [(time(h, m).strftime('%I:%M %p'), time(h, m).strftime('%I:%M %p')) for h in range(0,24) for m in (0, 30)]     
class OpeningHour(models.Model):

    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    day = models.IntegerField(choices=DAYS)
    from_hour = models.CharField(choices=HOURS_OF_DAY_24, max_length=10, blank=True)
    to_hour = models.CharField(choices=HOURS_OF_DAY_24, max_length=10, blank=True)
    is_closed = models.BooleanField(default=False)

    class Meta:
        ordering = ("day", "-from_hour")
        
    def __str__(self):
        return self.get_day_display()