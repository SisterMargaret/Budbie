from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.template.defaultfilters import slugify
from accounts.forms import UserProfileForm
from accounts.models import UserProfile
from django.contrib.auth.decorators import login_required, user_passes_test
from accounts.views import check_role_vendor
from menu.forms import CategoryForm, FoodItemForm
from menu.models import Category, FoodItem
from vendor.forms import VendorForm
from vendor.models import Vendor
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
            category.slug = slugify(category_name)
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
