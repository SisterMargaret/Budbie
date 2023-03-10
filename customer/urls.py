from django.urls import path, include
from accounts import views as accountViews
from . import views
urlpatterns = [
    path('', accountViews.customerDashboard, name="customerDashboard"),
    path('profile/', views.customerProfile, name="customerProfile"),
]