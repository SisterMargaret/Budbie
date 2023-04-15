import base64
import datetime
from accounts.utils import send_notification_email
from foodapp_main import settings
import qrcode
from qrcode.image.svg import SvgPathFillImage, SvgImage
import io
import simplejson as json
from accounts.models import User
from marketplace.models import Cart
from menu.models import FoodItem
from django.contrib.sites.shortcuts import get_current_site

from order.models import Order, OrderedFood, Payment

def generate_order_number(pk):
    current_datetime = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    order_number = current_datetime + str(pk)
    return order_number
    
def get_order_total_by_vendor(order, vendor):
    total_data = json.loads(order.total_data)
    data = total_data.get(str(vendor.id))
    
    subtotal=0
    tax = 0
    tax_dictionary= {}
    
    for key, val in data.items():
        
        subtotal += float(key)
        val = val.replace("'", '"')
        val = json.loads(val)
        tax_dictionary.update(val)

        for i in val:
            for j in val[i]:
                tax += float(val[i][j])
    grand_total = float(subtotal) + float(tax)
        
    return { 'subtotal' : subtotal,
            'total_tax' : tax, 
            'tax_dictionary' : tax_dictionary, 
            'grand_total' : round(grand_total,2)  }

def create_order_and_orderedItems(transaction_id, payment_method, status, metadata):
        
        order_number = metadata.order_number
        
        user = User.objects.get(id = metadata.user_id)
        
        #UPDATE THE ORDER STATUS
        order = Order.objects.get(order_number = order_number, user=user)
        
        #CREATE THE PAYMENT OBJECT
        payment = Payment(
            user = user,
            transaction_id = transaction_id,
            payment_method = payment_method,
            status = status,
            amount = metadata.order_total
        )
        payment.save()
        
        order.payment = payment
        order.is_ordered = True
        order.save()
        
        # #CREATE ORDERED FOOD ITEMS
        # cart_items = json.loads(metadata.json) #Cart.objects.filter(user=metadata.user) #This should be genereated from json
        # for item in cart_items:
        #     foodItem = FoodItem.objects.get(id=item)
        #     ordered_food = OrderedFood(
        #          order = order,
        #          payment = payment,
        #          user = user,
        #          foodItem = foodItem,
        #          quantity = int(cart_items[item]),
        #          price = foodItem.price,
        #          amount = foodItem.price * int(cart_items[item]),
        #         )
        #     ordered_food.save()
        # ****************
         #CREATE ORDERED FOOD ITEMS
        cart_items = Cart.objects.filter(user=user)
        for item in cart_items:
            ordered_food = OrderedFood(
                order = order,
                payment = payment,
                user = user,
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
            'user' : user,
            'order' : order,
            'to_email' : order.email,
            'foods': ordered_food,
            'domain': settings.CURRENT_SITE,
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
                    'user' : user,
                    'order' : order,
                    'to_email' : i.foodItem.vendor.user.email,
                    'foods': ordered_food_to_vendor,
                    'domain': settings.CURRENT_SITE,
                    'subtotal' : get_order_total_by_vendor(order, i.foodItem.vendor)['subtotal'],
                    'tax_data' : get_order_total_by_vendor(order, i.foodItem.vendor)['tax_dictionary'],
                    'grand_total' : get_order_total_by_vendor(order, i.foodItem.vendor)['grand_total'],
                }
            
                send_notification_email(mail_subject, mail_template, context)
            
            #CLEAR THE CART
            #print("clear the cart")
        cart_items.delete()
            
def getQRCode(request, order_number):
    current_url = get_current_site(request) + request.build_absolute_uri(f'/customer/order-details/{order_number}')
    factory = SvgImage
    qr_image = qrcode.make(current_url,image_factory=factory, box_size=20)    
    bufstore = io.BytesIO()
    qr_image.save(bufstore)    
    #return bufstore.getvalue().decode()
    base64_image = base64.b64encode(bufstore.getvalue()).decode()
    return 'data:image/svg+xml;utf8;base64,' + base64_image