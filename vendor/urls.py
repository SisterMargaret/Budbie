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
    path('menu-builder/category/delete/<int:pk>/', views.deleteCategory, name='deleteCategory')
]
