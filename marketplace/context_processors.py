from marketplace.models import Cart, Tax
from menu.models import FoodItem

def get_cart_counter(request):
    cart_count = 0
    if request.user.is_authenticated:
        try:
            cart_items = Cart.objects.filter(user=request.user)
            if cart_items:
                for cart_item in cart_items:
                    cart_count += cart_item.quantity
            else:
                cart_count = 0    
        except:
            cart_count = 0
    return dict(cart_count= cart_count,)

def get_cart_amount(request):
    vat_registered = False
    subtotal = 0
    tax = 0
    tax_dictionary = {}
    grand_total = 0
    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user)
        for item in cart_items:
            foodItem = FoodItem.objects.get(pk=item.foodItem.id)
            subtotal += (foodItem.price * item.quantity)
        
        if cart_items and cart_items.count() > 0:
           vat_registered = (cart_items[0].foodItem.vendor.vat_number != None) 
        
        if vat_registered:
            tax_to_apply = Tax.objects.filter(is_active = True)
            
            for i in tax_to_apply:
                tax_type = i.type
                tax_percentage = i.percentage
                tax_amount = round((tax_percentage * subtotal)/100,2)
                tax_dictionary.update({tax_type : {str(tax_percentage) : tax_amount}})
            
            tax = sum(x for key in tax_dictionary.values() for x in key.values() )                

        grand_total = subtotal + tax
        
    return dict(subtotal=subtotal, tax=tax, grand_total=grand_total, tax_dictionary=tax_dictionary)