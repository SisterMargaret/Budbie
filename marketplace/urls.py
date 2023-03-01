from django.urls import path
from . import views
from accounts import views as AccountViews

urlpatterns = [
    path('', views.marketplace, name='marketplace'),
    path('<slug:slug>/', views.vendorDetail, name="vendorDetail"),
    
    #Add to CART
    path('addToCart/<int:foodItemId>/', views.addToCart, name='addToCart'),
    #Decrease quantity of fooditem
    path('decreaseCart/<int:foodItemId>/', views.decreaseCart, name='decreaseCart'),
    
    #Deleting item from the cart
    path('deleteCartItem/<int:cartId>/', views.deleteCartItem, name='deleteCartItem')
]
