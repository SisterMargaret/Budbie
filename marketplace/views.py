from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from datetime import date, datetime
from marketplace.models import Cart
from marketplace.context_processors import get_cart_amount, get_cart_counter
from menu.models import Category, FoodItem
from django.db.models import Prefetch, Q
from vendor.models import OpeningHour, Vendor
from django.contrib.auth.decorators import login_required

from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.measure import D # ``D`` is a shortcut for ``Distance``
from django.contrib.gis.db.models.functions import Distance

# Create your views here.
def marketplace(request):
    vendors = Vendor.objects.filter(is_approved=True, user__is_active=True)
    vendor_count = vendors.count()
    context = {
        'vendors' : vendors,
        'vendor_count': vendor_count
    }
    return render(request, 'marketplace/listings.html', context)

def vendorDetail(request, slug):
    vendor = get_object_or_404(Vendor, slug=slug)
    categories = Category.objects.filter(vendor=vendor).prefetch_related(
        Prefetch('fooditems',
                 queryset= FoodItem.objects.filter(is_available = True)
                )
        
    )
    
    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user)
    else:        
        cart_items = None
    
    opening_hours = OpeningHour.objects.filter(vendor=vendor).order_by('day','-from_hour')
    today = date.today().isoweekday()
    current_day_hours = OpeningHour.objects.filter(vendor=vendor, day=today)
            
    context = {
        'vendor' : vendor,
        'categories' : categories,
        'cart_items' : cart_items,
        'opening_hours' : opening_hours,
        'current_day_hours' : current_day_hours,
    }
    return render(request, 'marketplace/vendor_detail.html', context)

def addToCart(request, foodItemId):
    if request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            try:
                foodItem = FoodItem.objects.get(id=foodItemId)
                try:
                    
                    checkCart = Cart.objects.get(user=request.user, foodItem=foodItem)
                    checkCart.quantity += 1
                    checkCart.save()
                    return JsonResponse({"status" : "Success", 
                                         "message": "Cart successfully incremented",
                                         "cart_counter" : get_cart_counter(request),
                                         'qty' : checkCart.quantity,
                                         "cart_amount": get_cart_amount(request)})
                except:
                    checkCart = Cart.objects.create(user=request.user, foodItem=foodItem, quantity=1)
                    
                    return JsonResponse({"status" : "Success", 
                                         "message": "Food Item added to the cart", 
                                         "cart_counter" :get_cart_counter(request), 
                                         "qty" : checkCart.quantity, 
                                         "cart_amount": get_cart_amount(request)})
            except:
                 return JsonResponse({"status" : "Failed", "message": "Food Item not available"})
        else:
            return JsonResponse({'status': 'Failed', 'message':'Invalid Request'})
    else:
        return JsonResponse({'status': 'login_required', 'message': 'Please login to continue'})
    
def decreaseCart(request, foodItemId):
    if request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            try:
                foodItem = FoodItem.objects.get(id=foodItemId)
                try:
                    
                    checkCart = Cart.objects.get(user=request.user, foodItem=foodItem)
                    
                    if checkCart.quantity > 1:
                        checkCart.quantity -= 1
                        checkCart.save()
                    else:
                        checkCart.delete()
                        checkCart.quantity = 0
                       
                    return JsonResponse({"status" : "Success", 
                                         "message": "Cart successfully incremented",
                                         "cart_counter" : get_cart_counter(request),
                                         'qty' : checkCart.quantity,
                                          "cart_amount": get_cart_amount(request)})
                except:
                    checkCart = Cart.objects.create(user=request.user, foodItem=foodItem, quantity=0)
                    
                    return JsonResponse({"status" : "Failed", 
                                         "message": "You do not have this item in your the cart", 
                                         "cart_counter" :get_cart_counter(request), 
                                         "qty" : checkCart.quantity,
                                          "cart_amount": get_cart_amount(request)})
            except:
                 return JsonResponse({"status" : "Failed", "message": "Food Item not available"})
        else:
            return JsonResponse({'status': 'Failed', 'message':'Invalid Request'})
    else:
        return JsonResponse({'status': 'login_required', 'message': 'Please login to continue'})

@login_required(login_url='login')   
def cart(request):
    cart_items = Cart.objects.filter(user=request.user).order_by('created_at')
    context = {
        'cart_items' : cart_items,
        
    }
    return render(request, 'marketplace/cart.html', context)

def deleteCartItem(request, cartId):
    if request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            try:
                foodCartItem = Cart.objects.get(user= request.user, id = cartId)
                if foodCartItem:
                    foodCartItem.delete()
                    return JsonResponse({'status': 'Success', 
                                         'message': 'Cart item has been deleted', 
                                         'cart_counter': get_cart_counter(request),
                                          "cart_amount": get_cart_amount(request)})
            except:
                    return JsonResponse({'status': 'Failed', 'message': 'Cart is empty'})
        else:
            return JsonResponse({'status': 'Failed', 'message': 'Invalid request!'})
    return JsonResponse({'status' : 'login_required', 'message':'Please login to continue'})

def search(request):
    
    if not 'address' in request.GET:
        return redirect('marketplace')
    else:
        address = request.GET['address']
        
        latitude = request.GET['lat']
        longitude = request.GET['long']
        radius = request.GET['radius']
        keyword = request.GET['keyword']
        # get vendor ids that
        foodItem_By_Category = FoodItem.objects.filter(food_title__icontains=keyword, is_available=True).values_list('vendor', flat=True)
        
        if latitude and longitude and radius:
            pnt = GEOSGeometry('POINT(%s %s)' %(longitude, latitude), srid=4326)
        
        vendors = Vendor.objects.filter(Q(id__in=foodItem_By_Category) | Q(vendor_name__icontains=keyword), 
                                        is_approved=True, 
                                        user__is_active=True,
                                        user_profile__location__distance_lte=(pnt, D(mi=radius))
                                        ).annotate(distance=Distance("user_profile__location", pnt)).order_by("distance")
        
        for v in vendors:
            v.mls = round(v.distance.mi,1)
        
        context = {
            'vendors' : vendors,
            'vendor_count' : vendors.count()
        }
        return render(request, 'marketplace/listings.html', context)