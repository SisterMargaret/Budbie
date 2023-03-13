from django.urls import path, include
from accounts import views as accountViews
from . import views
urlpatterns = [
    path('', accountViews.customerDashboard, name="customerDashboard"),
    path('profile/', views.customerProfile, name="customerProfile"),
    #CUSTOMER DASHBOARD
    path('my-orders/', views.myOrders, name="myOrders"),
    path('order-details/<str:order_number>/', views.orderDetails, name="orderDetails"),
]