from django.contrib import admin

from marketplace.models import Cart, Tax

class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'foodItem', 'quantity', 'created_at', 'updated_at')

class TaxAdmin(admin.ModelAdmin):
    list_display = ('type', 'percentage', 'is_active')

# Register your models here.
admin.site.register(Cart, CartAdmin)
admin.site.register(Tax, TaxAdmin)