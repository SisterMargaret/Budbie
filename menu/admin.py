from django.contrib import admin

from menu.models import Category, FoodItem

class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = { 'slug' : ('category_name',) }
    list_display = ('category_name', 'vendor',) 
    search_fields = ('category_name', 'vendor__vendor_name')

class FoodItemAdmin(admin.ModelAdmin):
    prepopulated_fields = { 'slug' : ('food_title',) }
    list_display = ('food_title','category','price','is_available')
    search_fields = ('food_title', 'category__category_name', 'vendor__vendor_name')
    list_filter = ('is_available','vendor__vendor_name')

# Register your models here.
admin.site.register(Category, CategoryAdmin)
admin.site.register(FoodItem, FoodItemAdmin)