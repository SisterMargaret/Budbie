from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.db import IntegrityError
from django.template.defaultfilters import slugify
from accounts.forms import UserProfileForm
from accounts.models import UserProfile
from django.contrib.auth.decorators import login_required, user_passes_test
from accounts.views import check_role_vendor
from menu.forms import CategoryForm, FoodItemForm
from menu.models import Category, FoodItem
from vendor.forms import OpeningHoursForm, VendorForm
from vendor.models import OpeningHour, Vendor
from vendor.utils import get_vendor



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

@login_required(login_url='login')
@user_passes_test(test_func=check_role_vendor)
def menuBuilder(request):
    vendor = get_vendor(request)
    categories = Category.objects.filter(vendor=vendor).order_by('created_at')
    context = {
        'categories' : categories
    }
    return render(request, 'vendor/menu_builder.html', context)

@login_required(login_url='login')
@user_passes_test(test_func=check_role_vendor)
def foodItemsByCategory(request, pk=None):
    vendor = get_vendor(request)
    category = get_object_or_404(Category, pk=pk)
    foodItems = FoodItem.objects.filter(vendor=vendor, category=category)
    
    context = {
        'foodItems' : foodItems,
        'category' : category
    }
    return render(request, 'vendor/foodItemsByCategory.html', context)

@login_required(login_url='login')
@user_passes_test(test_func=check_role_vendor)
def addCategory(request):
    if request.POST:
        form = CategoryForm(request.POST)
        
        if form.is_valid():
            category_name = form.cleaned_data['category_name']
            category = form.save(commit=False)
            category.vendor = get_vendor(request)
            form.save()
            category.slug = slugify(category_name) + '-'+str(category.id)
            form.save()
            messages.success(request, "Category added successfully")
            return redirect('menuBuilder')
        else:
            print(form.errors)
    else:
        form = CategoryForm()
    context = {
        'form' : form
    }
    return render(request, 'vendor/add_category.html', context)

@login_required(login_url='login')
@user_passes_test(test_func=check_role_vendor)
def editCategory(request, pk=None):
    category = get_object_or_404(Category, pk=pk)
    if request.POST:
            form = CategoryForm(request.POST, instance=category)

            if form.is_valid():
                category_name = form.cleaned_data['category_name']
                category = form.save(commit=False)
                category.vendor = get_vendor(request)
                category.slug = slugify(category_name)+'-'+str(category.id)
                form.save()
                messages.success(request, "Category updated successfully")
                return redirect('menuBuilder')
            else:
                print(form.errors)
    else:
            form = CategoryForm(instance=category)
    context = {
        'form' : form,
        'category' : category
    }
    return render(request, 'vendor/edit_category.html', context)

@login_required(login_url='login')
@user_passes_test(test_func=check_role_vendor)
def deleteCategory(request, pk=None):
    category = get_object_or_404(Category, pk=pk)
    category.delete()
    messages.success(request, "Category has been deleted successfully")
    return redirect('menuBuilder')

@login_required(login_url='login')
@user_passes_test(test_func=check_role_vendor)
def addFoodItem(request):
    if request.POST:
        form = FoodItemForm(request.POST, request.FILES)
        
        if form.is_valid():
            food_title = form.cleaned_data['food_title']
            foodItem = form.save(commit=False)
            foodItem.vendor = get_vendor(request)
            foodItem.slug = slugify(food_title)+'-'+str(foodItem.id)
            form.save()
            messages.success(request, "Food Item added successfully")
            return redirect('foodItemsByCategory', foodItem.category.id)
        else:
            print(form.errors)
    else:
        form = FoodItemForm()
    form.fields['category'].queryset=Category.objects.filter(vendor=get_vendor(request))
    context = {
        'form' : form
    }
    return render(request, 'vendor/add_foodItem.html', context)

@login_required(login_url='login')
@user_passes_test(test_func=check_role_vendor)
def editFoodItem(request, pk=None):
    foodItem = get_object_or_404(FoodItem, pk=pk)
    if request.POST:
            form = FoodItemForm(request.POST, request.FILES, instance=foodItem)

            if form.is_valid():
                food_title = form.cleaned_data['food_title']
                foodItem = form.save(commit=False)
                foodItem.vendor = get_vendor(request)
                foodItem.slug = slugify(food_title)
                form.save()
                messages.success(request, "FoodItem updated successfully")
                return redirect('foodItemsByCategory', foodItem.category.id)
            else:
                print(form.errors)
    else:
            form = FoodItemForm(instance=foodItem)
    form.fields['category'].queryset=Category.objects.filter(vendor=get_vendor(request))
    context = {
        'form' : form,
        'foodItem' : foodItem 
    }
    return render(request, 'vendor/edit_FoodItem.html', context)

@login_required(login_url='login')
@user_passes_test(test_func=check_role_vendor)
def deleteFoodItem(request, pk=None):
    foodItem = get_object_or_404(FoodItem, pk=pk)
    foodItem.delete()
    messages.success(request, "Food Item has been deleted successfully")
    return redirect('foodItemsByCategory', foodItem.category.id)


def openingHours(request):
    opening_hours = OpeningHour.objects.filter(vendor=get_vendor(request))
    form = OpeningHoursForm()
    context = {
        'form' : form,
        'opening_hours' : opening_hours
    }
    return render(request, 'vendor/opening_hours.html', context)

def addOpeningHours(request):
    if request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == 'POST':
            day = request.POST['day']
            from_hour = request.POST['from_hour']
            to_hour = request.POST['to_hour']
            is_closed = request.POST['is_closed'] == 'true'
            
            print(day, from_hour, to_hour, is_closed)
            
            try:
                hour = OpeningHour.objects.create(vendor = get_vendor(request),
                                                  day = day,
                                                  from_hour = from_hour,
                                                  to_hour = to_hour,
                                                  is_closed = is_closed)
                if hour:
                    day = OpeningHour.objects.get(id=hour.id)
                    if day.is_closed:
                        response = {'status' : 'Success', 
                                    'id' : hour.id, 
                                    'day': day.get_day_display(), 
                                    'is_closed' : 'Closed'}
                    else:
                        response = {'status' : 'Success', 
                                    'id' : hour.id, 
                                    'day': day.get_day_display(), 
                                    'from_hour' : hour.from_hour, 
                                    'to_hour' : hour.to_hour}
                        
                return JsonResponse(response)
            except IntegrityError as e:
                return JsonResponse({'status' : 'Failed', 'message' : f"Error adding opening hours. {from_hour} - {to_hour} already exist for this day" })
            
        else:
           return JsonResponse({'status' : 'Failed', 'message':'Invalid Request'}) 
  
    return JsonResponse({'status' : 'login_required', 'message':'Please login to continue'})

def deleteOpeningHours(request, pk):
    if request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == 'POST':
            openingHour = get_object_or_404(OpeningHour, id = pk)
            openingHour.delete()
            messages.success(request, 'Opening hours have been deleted')
    
    return JsonResponse({'status' : 'Success', 'message':'Please login to continue'})