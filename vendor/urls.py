from django.urls import path, include
from . import views
from accounts import views as AccountViews

urlpatterns = [
    path('', AccountViews.vendorDashboard, name='vendor'),
    path('profile/', views.vendorProfile, name='vendorProfile'),
    path('menu-builder/', views.menuBuilder, name='menuBuilder'),
    path('menu-builder/category/<int:pk>/', views.foodItemsByCategory, name='foodItemsByCategory'),
    
    #Category CRUD
    path('menu-builder/category/add/', views.addCategory, name='addCategory'),
    path('menu-builder/category/edit/<int:pk>/', views.editCategory, name='editCategory'),
    path('menu-builder/category/delete/<int:pk>/', views.deleteCategory, name='deleteCategory'),
    
    #FoodItem CRUD
    path('menu-builder/food/add/', views.addFoodItem, name='addFoodItem'),
    path('menu-builder/food/edit/<int:pk>/', views.editFoodItem, name='editFoodItem'),
    path('menu-builder/food/delete/<int:pk>/', views.deleteFoodItem, name='deleteFoodItem'),
    
    #Opening Hours
    path('opening-hours/', views.openingHours, name='openingHours'),
    path('opening-hours/add/', views.addOpeningHours, name='addOpeningHours'),
    path('opening-hours/delete/<int:pk>/', views.deleteOpeningHours, name='deleteOpeningHours'),
    
    path('order_detail/<str:order_number>/', views.orderDetail, name="vendorOrderDetail"),
    
    path('my-orders/', views.myOrders, name='vendorMyOrders'),
    
]
