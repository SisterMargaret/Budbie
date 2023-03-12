from django.contrib import admin

from order.models import Order, OrderedFood, Payment

class OrderFoodItemInline(admin.TabularInline):
    model = OrderedFood
    readonly_fields = ('order', 'payment', 'user', 'foodItem', 'quantity', 'price', 'amount')
    extra = 0

class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'name', 'phone', 'email', 'total', 'payment_method', 'status', 'is_ordered']
    inlines = [OrderFoodItemInline]

# Register your models here.
admin.site.register(Payment)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderedFood)