from time import sleep
from django.shortcuts import render, redirect
from accounts.utils import send_notification_email
from foodapp_main import settings
from marketplace.context_processors import get_cart_amount
from marketplace.models import Cart, Tax 
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.http import JsonResponse
from order.forms import OrderForm
from order.models import Order, OrderedFood, Payment
import simplejson as json
import stripe
from order.utils import generate_order_number, get_order_total_by_vendor, getQRCode

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
    
    cart_items_json={}
    for it in cart_items:
        cart_items_json.update({"{}".format(it.foodItem.id) :  "{}".format(it.quantity)})
    
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
            order.payment_method = 'Stripe'
            
            order.save()
            order.order_number = generate_order_number(order.id)
            order.vendors.add(*vendor_ids)
            order.save()
            
            #print(cart_items_json)
            
            context = {
                'order' : order,
                'cart_items' : cart_items,
                'cart_items_json' : cart_items_json,
                'client_secret':'',
                'stripe_secret' : settings.STRIPE_PUB_KEY
            }
            
            #Stripe Payment
                
            stripe.api_key = settings.STRIPE_SECRET_KEY
            
            payment_intent = stripe.PaymentIntent.create(
                                amount=int(order.total * 100),
                                currency='gbp',
                                automatic_payment_methods={"enabled": True},
                                capture_method="manual", #allows to place hold on the payment
                                #on_behalf_of='acct_1HYGocIWUKRSbB8m',
                                transfer_data = {"destination": cart_items[0].foodItem.vendor.payment_account_key},
                                metadata = {'json': json.dumps(cart_items_json), 
                                            'order_number' : order.order_number,
                                            'order_total': order.total,
                                            'user_id' : order.user.id,
                                            }
                                
                            );    
            context['client_secret'] = payment_intent.client_secret
            context['paymentIntent'] = payment_intent.id
                
               #print(context)

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
            payment_method = 'Stripe'
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
            #print("clear the cart")
            cart_items.delete()
            
            #Return the status
            
    return JsonResponse({"status" : "Success", 
                         'order_number' : order_number,
                         'transaction_id' : transaction_id})

def getOrder(request):
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        order_number = request.POST['order_number']
        transaction_id = request.POST['transaction_id'] 
        orders = Order.objects.filter(order_number=order_number, payment__transaction_id=transaction_id, is_ordered=True)
        print(orders.count())
        if orders.count() == 0:
            return JsonResponse({"status" : "Failed", 
                                        'order_number' : order_number,
                                        'transaction_id' : transaction_id})
        return JsonResponse( {"status" : orders.first().status}, status=200)
    return JsonResponse(status=400)

def orderComplete(request):
    order_number = request.GET['order_no']
    transaction_id = request.GET['transaction_id']
    #Too fast for the redirect to get the order
    sleep(0.3)
    # try:
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
            'tax_data' : tax_data,
            'qr_svg' : getQRCode(request, order.order_number),
        }
    return render(request, 'order/orderComplete.html', context)
    # except:
    #     print('exception occured')
    
def stripePlaceOrder(request):
    cart_items = Cart.objects.filter(user=request.user).order_by('created_at')
    cart_count = cart_items.count()
    
    if cart_count <= 0:
        return redirect('marketplace')
    
    stripe.api_key = settings.STRIPE_SECRET_KEY
    payment_intent = stripe.PaymentIntent.create(
                                amount=1000,
                                currency='gbp',
                                automatic_payment_methods={"enabled": True},
                                capture_method="manual", #allows to place hold on the payment
                                #on_behalf_of='acct_1HYGocIWUKRSbB8m',
                                transfer_data = {"destination": "acct_1MsPmxIIEzOr8uuC"},
                            );    
    context = {
         'client_secret' : payment_intent.client_secret,
         'paymentIntent' : payment_intent.id
     }
    
    return render(request, 'order/stripePlaceOrder.html', context)

def updateOrderStatus(request):
    if request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            order_number = request.POST['order_number']
            status = request.POST['newstatus']
            #reason = request.POST['reason']        

            order = Order.objects.get(order_number=order_number, is_ordered=True)
            
            #requested_by_customer, or 

            stripe.api_key = settings.STRIPE_SECRET_KEY
            paymentIntent = stripe.PaymentIntent.retrieve(order.payment.transaction_id)
            if paymentIntent and paymentIntent.status == 'requires_capture' and status == 'Accepted':
                #Capture the payment if accepted
                #application fee amount should be in pence so multiplying with 100 to convert
                paymentIntent = stripe.PaymentIntent.capture(order.payment.transaction_id, 
                                                                application_fee_amount=(order.total*settings.HUNGRYBUFF_FEE/100)*100)
                if paymentIntent.status == "succeeded":
                    order.status = status
                    order.save()
                    return JsonResponse({'status': 'Success', 'newStatus' : status, 
                                 'message' : f"Order {str.lower(status)} successfully."}) 
                else:
                    return JsonResponse({'status': 'Fail', 
                                         'newStatus' : 'Payment Error!', 
                                         'message' : "Order payment could not be processed. Please contact the customer."}) 
            elif status == 'Rejected' and paymentIntent and paymentIntent.status == 'requires_capture':
                 paymentIntent = stripe.PaymentIntent.cancel(order.payment.transaction_id, 
                                                                cancellation_reason='abandoned')
                 if paymentIntent.status == "canceled":
                     order.status = status
                     order.save() 
                     return JsonResponse({'status': 'Success', 
                                          'newStatus' : status, 
                                          'message' : f"Order {str.lower(status)} successfully."})
            elif status == 'Ready':
                 order.status = status
                 order.save() 
                 return JsonResponse({'status': 'Success', 
                                          'newStatus' : status, 
                                          'message' : f"Order is now {str.lower(status)} for collection."})
            elif status == 'Collected':
                 order.status = status
                 order.save() 
                 return JsonResponse({'status': 'Success', 
                                          'newStatus' : status, 
                                          'message' : f"Order {str.lower(status)} successfully."})
                 
    return JsonResponse({'status': 'Fail', 'message' : f"Order could not be {str.lower(status)}"}) 

