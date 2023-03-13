from django.urls import path
from . import views


urlpatterns = [
    path('place-order/', views.placeOrder, name="placeOrder"),
    path('payment/', views.payment, name="payment"),   
    path('order-complete/', views.orderComplete, name="orderComplete"),
    
]