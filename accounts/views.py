import datetime
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.tokens import default_token_generator
from accounts.forms import UserForm
from accounts.models import User, UserProfile
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required, user_passes_test
from accounts.utils import detectUser, send_verification_email
from django.core.exceptions import PermissionDenied
from foodapp_main import settings
from order.models import Order
from vendor.forms import VendorForm
from django.utils.http import urlsafe_base64_decode
from django.template.defaultfilters import slugify
from vendor.models import Vendor
import stripe
import locale

# Restrict the vendor from accessing the customer dashboard
def check_role_vendor(user):
    if user.role == 1:
        return True
    raise PermissionDenied

# Restrict the customer from accessing the vendor dashboard
def check_role_customer(user):
    if user.role == 2:
        return True
    raise PermissionDenied


def registerUser(request):
    if request.user.is_authenticated:
        messages.warning(request, 'You are already logged in')
        return redirect('dashboard')
    
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
            
            #Send verification email
            send_verification_email(request, user)
            
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
    if request.user.is_authenticated:
        messages.warning(request, 'You are already logged in')
        return redirect('myAccount')
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
            vat_number = form.cleaned_data['vat_number']
            user = User.objects.create_user(first_name=first_name,
                                     last_name=last_name,
                                     username=username,
                                     email=email,
                                     password=password)
            user.role = User.VENDOR
            user.save()
            vendor = vendor_form.save(commit=False)
            vendor.user = user
            vendor.slug = slugify(vendor_form.cleaned_data['vendor_name'])+'-'+str(user.id)
            vendor.vat_number = vat_number
            user_profile = UserProfile.objects.get(user=user)
            vendor.user_profile = user_profile
            vendor.save()
            
            #Send verification email
            send_verification_email(request, user, 'Please activate your account','accounts/emails/account_verification_email.html')
            
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

def activate(request, uidb64, token):
    
    #Activate the user by setting the is_activate status true
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Congratulations! your account is activated')
        return redirect('myAccount')
    else:
        messages.error(request, 'Invalid activation link')
        return redirect('myAccount')

def login(request):
    if request.user.is_authenticated:
        messages.warning(request, 'You are already logged in')
        return redirect('myAccount')
        
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        
        user = auth.authenticate(email=email, password=password)
        
        if user is not None:
            auth.login(request, user)
            messages.success(request, "You are now logged in!")
            return redirect('myAccount')
        else:
            messages.error(request, "Invalid login credentials")
            return redirect('login')

    return render(request, 'accounts/login.html')

@login_required(login_url='login')
def logout(request):
    auth.logout(request)
    messages.info(request, "You have been logged out")
    return render(request, 'accounts/login.html')

@login_required(login_url='login')
@user_passes_test(check_role_customer)
def customerDashboard(request):
    orders = Order.objects.filter(user=request.user).order_by("-created_at")[:5]
    orders_count = Order.objects.filter(user=request.user).count()
    context = {
        'orders' : orders,
        'order_count' : orders_count
    }
    return render(request, 'accounts/customerDashboard.html', context)

@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def vendorDashboard(request):
    vendor = Vendor.objects.get(user=request.user)
    orders = Order.objects.filter(vendors__in=[vendor.id], is_ordered=True).order_by('-created_at')
    orders_count = orders.count()
    
    #total_revenue
    total_revenue = 0
    for i in orders:
        total_revenue += i.get_total_by_vendor()['grand_total']
    
    #Revenue this month
    current_month_revenue = 0
    current_month = datetime.datetime.now().month
    current_month_orders = orders.filter(vendors__in=[vendor.id], created_at__month = current_month)
    for i in current_month_orders:
        current_month_revenue += i.get_total_by_vendor()['grand_total']
    
    #Check if the vendor's account is setup properly in Stripe
    stripe_setup_fine = vendor.is_stripe_setup_complete()
    
    # locale.setlocale(locale.LC_ALL,)            
    
    context = {
        'vendor' : vendor,
        'stripe_setup' : stripe_setup_fine,
        'orders_count' : orders_count,
        'orders' : orders[:10],
        'total_revenue' : total_revenue,
        'current_month_revenue' : current_month_revenue,
    }
    return render(request, 'accounts/vendorDashboard.html', context)

@login_required(login_url='login')
def myAccount(request):
    user = request.user
    redirecturl = detectUser(user)
    return redirect(redirecturl)

def forgotPassword(request):
    if request.POST:
        email = request.POST['email']
        
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            
            #send verification email
            send_verification_email(request, user, 'Reset your password', 'accounts/emails/reset_password_email.html')
            messages.success(request, 'Password reset email has been sent')
            return redirect('login')
        else:
            messages.error(request, 'Account does not exists')
            return redirect('forgotPassword') 
               
    return render(request, 'accounts/forgotPassword.html')


def resetPassword(request):
    
    if request.POST:
        
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        if password == confirm_password:
            uid = request.session.get('uid')
            user = User.objects.get(pk = uid)
            user.set_password(password)
            user.is_active = True
            user.save()
            messages.success(request, 'Password reset successfully')
            return redirect('login')
        else:
            messages.error(request, "Passwords do not match")
            return redirect('resetPassword')
    
    return render(request, 'accounts/resetPassword.html')


def resetPasswordValidate(request, uidb64, token):
    
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    
    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.info(request, 'Please reset your password')
        return redirect('resetPassword')
    else:
        messages.error(request, 'Invalid link')
        return redirect('myAccount')
    
def onboarding(request):
    return_url = ("%s://%s" % (request.scheme, request.get_host()))
    
    stripe.api_key = settings.STRIPE_SECRET_KEY
    vendor = Vendor.objects.get(user=request.user)
    
    if not vendor.payment_account_key:
        # #Creates express account
        account =  stripe.Account.create(type="express", 
                                        email=vendor.user.email,
                                        business_profile={
                                                'name': vendor.vendor_name,
                                                'support_email': vendor.user.email,
                                                'support_address' : {
                                                    'line1' : vendor.user_profile.address,
                                                    'state' : vendor.user_profile.state,
                                                    'city' : vendor.user_profile.city,
                                                    'postal_code' : vendor.user_profile.postcode,
                                                }
                                            },
                                        country='GB',
                                        settings={
                                                    'payouts' : 
                                                        {
                                                            'schedule': {'interval' : 'weekly',
                                                                            'weekly_anchor' : 'friday'
                                                                        },
                                                        }
                                                }
                                        )
        vendor.payment_account_key = account.id
        vendor.save()
        print('inside new account key')
    else:
        account = stripe.Account.retrieve(id=vendor.payment_account_key)


    #Create onboarding url link
    onboarding = stripe.AccountLink.create(
                account=account.id,
                refresh_url=f"{return_url}/login",
                return_url=f"{return_url}/vendorDashboard",
                type="account_onboarding",
            )
    
    return redirect(onboarding.url)