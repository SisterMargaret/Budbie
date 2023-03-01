from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404
from marketplace.models import Cart
from marketplace.context_processors import get_cart_amount, get_cart_counter
from menu.models import Category, FoodItem
from django.db.models import Prefetch
from vendor.models import Vendor
from django.contrib.auth.decorators import login_required

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
    
    context = {
        'vendor' : vendor,
        'categories' : categories,
        'cart_items' : cart_items
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