from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from accounts.forms import UserProfileForm
from accounts.models import UserProfile
from django.contrib.auth.decorators import login_required, user_passes_test
from accounts.views import check_role_vendor
from vendor.forms import VendorForm
from vendor.models import Vendor

@login_required(login_url='login')
@user_passes_test(test_func=check_role_vendor)
# Create your views here.
def vendorProfile(request):
    profile = get_object_or_404(UserProfile, user=request.user)
    vendor = get_object_or_404(Vendor, user=request.user)
    
    if request.method == 'POST':
        userProfileForm = UserProfileForm(request.POST, request.FILES, instance=profile)
        vendorForm = VendorForm(request.POST, request.FILES, instance=vendor)
        
        if userProfileForm.is_valid() and userProfileForm.is_valid():
           userProfileForm.save()
           vendorForm.save()
           messages.success(request, "Settings updated")
           return redirect('vendorProfile')     
        else:
            print(userProfileForm.errors)
            print(vendorForm.errors)
    else:   
        userProfileForm = UserProfileForm(instance=profile)
        vendorForm = VendorForm(instance=vendor)
        
    context = {
        'profileForm' : userProfileForm,
        'vendorForm' : vendorForm,
        'vendor' : vendor,
        'profile' : profile
    }
    return render(request, 'vendor/vendor_profile.html', context)