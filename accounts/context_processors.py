from accounts.models import UserProfile
from vendor.models import Vendor
from django.conf import settings

def get_vendor(request):
    try:
        vendor = Vendor.objects.get(user=request.user)
        
    except:
        vendor = None
    return dict(vendor=vendor)

def get_user_profile(request):
    try:
        userProfile = UserProfile.objects.get(user=request.user)
    except:
        userProfile = None
    return dict(user_profile=userProfile)

def get_google_api(request):
    return {'GOOGLE_API_KEY': settings.GOOGLE_API_KEY}

def get_paypal_clientid(request):
    return {'PAYPAL_CLIENT_ID': settings.PAYPAL_CLIENT_ID}

# def get_stripe_client_key(request):
#     return {'STRIPE_CLIENT_KEY': settings.STRIPE_SECRET_KEY}