from django.urls import path
from . import views


urlpatterns = [
    path('place-order/', views.placeOrder, name="placeOrder"),
    path('stripe-place-order/', views.stripePlaceOrder, name="stripePlaceOrder"),
    path('payment/', views.payment, name="payment"),   
    path('orderStatus/', views.getOrder, name="orderStatus"),   
    path('order-complete/', views.orderComplete, name="orderComplete"),
    path('update-order-status/', views.updateOrderStatus, name="updateOrderStatus"),
    
]