from django.shortcuts import render, redirect
from accounts.utils import send_notification_email
from marketplace.context_processors import get_cart_amount
from marketplace.models import Cart, Tax 
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.http import JsonResponse
from order.forms import OrderForm
from order.models import Order, OrderedFood, Payment
import simplejson as json

from order.utils import generate_order_number, get_order_total_by_vendor

@login_required(login_url='login') 
def placeOrder(request):
    
    cart_items = Cart.objects.filter(user=request.user).order_by('created_at')
    cart_count = cart_items.count()
    
    if cart_count <= 0:
        return redirect('marketplace')
 
    vendor_ids = []
    for i in cart_items:
        if i.foodItem.vendor.id not in vendor_ids:
            vendor_ids.append(i.foodItem.vendor.id)
 
    
    get_tax = Tax.objects.filter(is_active=True)
    k = {}
    subtotal = 0
    tax_dictionary = {}
    total_data={}
    for i in cart_items:
        vendorId = i.foodItem.vendor.id
        if vendorId in k:
            subtotal = k[vendorId]
            subtotal += (i.foodItem.price * i.quantity)
            k[vendorId] = subtotal
        else:
            subtotal += (i.foodItem.price * i.quantity)
            k[vendorId] = subtotal
    
        tax_dictionary = {}
        for i in get_tax:
            tax_type = i.type
            tax_percentange = i.percentage
            tax_amount = round((tax_percentange * subtotal)/100, 2)
            tax_dictionary.update({ tax_type: {str(tax_percentange) : str(tax_amount)}})
        
        #Contruct total data
        total_data.update({vendorId : {str(subtotal) : str(tax_dictionary)}})
     
    dicCart = get_cart_amount(request)
    subtotal = dicCart['subtotal']   
    totalTax = dicCart['tax']
    grandTotal = dicCart['grand_total']   
    tax_data = dicCart['tax_dictionary']
    
    if request.method == 'POST':
        form = OrderForm(request.POST)
        
        if form.is_valid():
            order = Order()
            order.first_name = form.cleaned_data['first_name']
            order.last_name = form.cleaned_data['last_name']
            order.phone = form.cleaned_data['phone']
            order.email = form.cleaned_data['email']
            order.address = form.cleaned_data['address']
            order.city = form.cleaned_data['city']
            order.state = form.cleaned_data['state']
            order.country = form.cleaned_data['country']
            order.postcode = form.cleaned_data['postcode']
            order.user = request.user
            order.total = grandTotal
            order.tax_data = json.dumps(tax_data)
            order.total_data = json.dumps(total_data)
            order.total_tax = totalTax
            order.payment_method = request.POST['payment_method']
            
            order.save()
            order.order_number = generate_order_number(order.id)
            order.vendors.add(*vendor_ids)
            order.save()
            context = {
                'order' : order,
                'cart_items' : cart_items
            }
            return render(request, 'order/placeOrder.html', context)
        else:
            print(form.errors)
    
    return render(request, 'order/placeOrder.html')

@login_required(login_url='login')
def payment(request):
    if request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            order_number = request.POST['order_number']
            transaction_id = request.POST['transaction_id']
            payment_method = request.POST['payment_method']
            status = request.POST['status']
            
            #UPDATE THE ORDER STATUS
            order = Order.objects.get(order_number = order_number, user=request.user)
            
            #CREATE THE PAYMENT OBJECT
            payment = Payment(
                user = request.user,
                transaction_id = transaction_id,
                payment_method = payment_method,
                status = status,
                amount = order.total
                
            )
            payment.save()
            
            order.payment = payment
            order.is_ordered = True
            order.save()
            
            #CREATE ORDERED FOOD ITEMS
            cart_items = Cart.objects.filter(user=request.user)
            for item in cart_items:
                ordered_food = OrderedFood(
                    order = order,
                    payment = payment,
                    user = request.user,
                    foodItem = item.foodItem,
                    quantity = item.quantity,
                    price = item.foodItem.price,
                    amount = item.foodItem.price * item.quantity,
                )
                ordered_food.save()
            
            #SEND EMAIL NOTIFICATION TO THE CUSTOMER
            mail_subject = f'Thank you for your order'
            mail_template = "order/emails/order_confirmation.html"
            
            ordered_food = OrderedFood.objects.filter(order=order)
            customer_subtotal = 0
            for item in ordered_food:
                customer_subtotal += (item.price * item.quantity)
            
            
            tax_data = json.loads(order.tax_data)
            
            context = {
                'user' : request.user,
                'order' : order,
                'to_email' : order.email,
                'foods': ordered_food,
                'domain': get_current_site(request),
                'subtotal' : round(customer_subtotal,2),
                'tax_data' : tax_data,
            }
            
            send_notification_email(mail_subject, mail_template, context)
            
            #SEND EMAIL NOTIFICATIONS TO VENDORS
            mail_subject = f"New order received {order.order_number}"
            mail_template = "order/emails/new_order_received.html"
            to_emails = []
            
            for i in cart_items:
                if i.foodItem.vendor.user.email not in to_emails:
                    to_emails.append(i.foodItem.vendor.user.email)

                    ordered_food_to_vendor =   OrderedFood.objects.filter(order=order, foodItem__vendor=i.foodItem.vendor)
                    
                    context = {
                        'user' : request.user,
                        'order' : order,
                        'to_email' : i.foodItem.vendor.user.email,
                        'foods': ordered_food_to_vendor,
                        'domain': get_current_site(request),
                        'subtotal' : get_order_total_by_vendor(order, i.foodItem.vendor)['subtotal'],
                        'tax_data' : get_order_total_by_vendor(order, i.foodItem.vendor)['tax_dictionary'],
                        'grand_total' : get_order_total_by_vendor(order, i.foodItem.vendor)['grand_total'],
                    }
                
                    send_notification_email(mail_subject, mail_template, context)
            
            #CLEAR THE CART
            cart_items.delete()
            
            #Return the status
            
    return JsonResponse({"status" : "Success", 
                         'order_number' : order_number,
                         'transaction_id' : transaction_id})

def orderComplete(request):
    order_number = request.GET['order_no']
    transaction_id = request.GET['transaction_id']
    
    try:
        order = Order.objects.get(order_number=order_number, payment__transaction_id=transaction_id, is_ordered=True)
        orderedFood = OrderedFood.objects.filter(order=order)
        
        subtotal = 0
        for item in orderedFood:
            subtotal += (item.price * item.quantity)
        
        
        tax_data = json.loads(order.tax_data)
        
        context = {
                'order' : order,
                'orderedFood' : orderedFood,
                'subtotal' : subtotal,
                'tax_data' : tax_data
            }
        return render(request, 'order/orderComplete.html', context)
    except:
        return redirect('home')