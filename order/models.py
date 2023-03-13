from django.db import models

from accounts.models import User
from menu.models import FoodItem
from vendor.models import Vendor
import simplejson as json

request_object='' #Will be filled in by middleware
class Payment(models.Model):
    PAYMENT_METHOD = (('PayPal', 'PayPal'),
                      ('RazorPay', 'RazorPay'),
                      ('ApplePay', 'ApplePay'),
                      ('GooglePay', 'GooglePay'),
                      )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    transaction_id = models.CharField(max_length=100)
    payment_method = models.CharField(choices=PAYMENT_METHOD, max_length=100)
    amount = models.CharField(max_length=10)
    status = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.transaction_id

class Order(models.Model):
    STATUS = (
        ('New', 'New'),
        ('Accepted', 'Accepted'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    )
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, blank=True, null=True)
    vendors = models.ManyToManyField(Vendor, blank=True)
    order_number = models.CharField(max_length=20)
    first_name = models.CharField(max_length=50)
    last_name =  models.CharField(max_length=50)
    phone = models.CharField(max_length=15, blank=True)
    email = models.EmailField(max_length=254)
    address = models.CharField(max_length=250) 
    country = models.CharField(max_length=15, blank=True)
    state = models.CharField(max_length=15, blank=True)
    city = models.CharField(max_length=50)
    postcode = models.CharField(max_length=20)
    total = models.FloatField()
    tax_data = models.JSONField(blank=True, null=True, help_text="Data format: {'type' : {'percentage':'amount'}}")
    total_data = models.JSONField(blank=True, null=True)
    total_tax = models.FloatField()
    payment_method = models.CharField(max_length=25)
    status = models.CharField(max_length=15, choices=STATUS, default='New')
    is_ordered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at= models.DateTimeField(auto_now=True)
    
    @property
    def name(self):
        return f'{self.first_name}-{self.last_name}'
    
    def order_placed_to(self):
        return ",".join([str(i) for i in self.vendors.all()])
    
    #Refactor later
    def get_total_by_vendor(self):
        vendor = Vendor.objects.get(user=request_object.user)
        subtotal = 0
        tax = 0
        tax_dictionary = {}
        if self.total_data:
            total_data = json.loads(self.total_data)
            data = total_data.get(str(vendor.id)) 

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
    
    def __str__(self):
        return self.order_number
    
class OrderedFood(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    foodItem = models.ForeignKey(FoodItem, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.FloatField()
    amount = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.foodItem.food_title