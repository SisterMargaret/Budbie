import simplejson as json
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from accounts.forms import UserInfoForm, UserProfileForm
from accounts.models import User, UserProfile
from order.models import Order, OrderedFood

@login_required(login_url='login' )
def customerProfile(request):
    userProfile = get_object_or_404(UserProfile, user=request.user)
    
    if request.method == 'POST':
        profile_form = UserProfileForm(request.POST, request.FILES, instance=userProfile)
        userInfo_form = UserInfoForm(request.POST, instance=request.user)
        if profile_form.is_valid() and userInfo_form.is_valid():
            profile_form.save()
            userInfo_form.save()
            messages.success(request, 'Profile updated')
            return redirect('customerProfile') 
        else:
            print(profile_form.errors)
            print(userInfo_form.errors)
    else:
        profile_form = UserProfileForm(instance=userProfile)
        userInfo_form= UserInfoForm(instance=request.user)
        
    context = {
        'userInfoForm' : userInfo_form,
        'profileForm' : profile_form, 
        'profile' : userProfile
        
    } 
    return render(request, 'customer/customerProfile.html', context)

def myOrders(request):
    orders  = Order.objects.filter(user=request.user).order_by('-created_at')
    context = {
        'orders': orders
    }
    
    return render(request, 'customer/my_orders.html', context)

def orderDetails(request, order_number):
    try:
        order = Order.objects.get(order_number = order_number, is_ordered=True)
        orderedFood = OrderedFood.objects.filter(order=order)
    
        subtotal = 0
        for item in orderedFood:
            subtotal += (item.price* item.quantity)
            
        tax_data = json.loads( order.tax_data)
        
        context = {
            'order' : order,
            'orderedFood': orderedFood,
            'subtotal' : subtotal,
            'tax_data' : tax_data
        }
        return render(request, 'customer/order_details.html', context)
    except:
        return redirect('customer')
    
    