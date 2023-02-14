from django.http import HttpResponse
from django.shortcuts import render, redirect

from accounts.forms import UserForm
from accounts.models import User, UserProfile
from django.contrib import messages

from vendor.forms import VendorForm

# Create your views here.
def registerUser(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            # user = form.save(commit=False)
            # user.role = User.CUSTOMER
            # form.save()
            #Create user using create_user method
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = User.objects.create_user(first_name=first_name,
                                     last_name=last_name,
                                     username=username,
                                     email=email,
                                     password=password)
            user.role = User.CUSTOMER
            user.save()
            messages.success(request, 'Your user account has been successful')
            print('User Created')
            return redirect('registerUser')
        else:
            print(form.errors)
    else:
        form = UserForm()
    context = {
        'form' : form
    }
    return render(request, 'accounts/registerUser.html', context)

def registerVendor(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        vendor_form = VendorForm(request.POST, request.FILES)
        if form.is_valid() and form.is_valid():
            #Create user using create_user method
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = User.objects.create_user(first_name=first_name,
                                     last_name=last_name,
                                     username=username,
                                     email=email,
                                     password=password)
            user.role = User.VENDOR
            user.save()
            vendor = vendor_form.save(commit=False)
            vendor.user = user
            user_profile = UserProfile.objects.get(user=user)
            vendor.user_profile = user_profile
            vendor.save()
            messages.success(request, 'Your account has been registered successfully! Please wait for the approval')
            return redirect('registerVendor')
        else:
            print(form.errors)
    else:
        form = UserForm()
        vendor_form = VendorForm()
    
    context = {
        'form' : form,
        'vendor_form' : vendor_form
    }
    
    return render(request, 'accounts/registerVendor.html', context)