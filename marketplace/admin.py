from django.contrib import admin

from marketplace.models import Cart

class CartAdmin(admin.ModelAdmin):
    list_display = ['user', 'foodItem', 'quantity', 'created_at', 'updated_at']

# Register your models here.
admin.site.register(Cart, CartAdmin)