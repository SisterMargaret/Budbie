
from django.shortcuts import HttpResponse

from django.shortcuts import render
from django.http import HttpResponse

from vendor.models import Vendor

def home(request):
    approved_vendors= Vendor.objects.filter(is_approved=True, user__is_active=True)[:8]
    context = {
        'vendors' : approved_vendors
    }
    return render(request, 'home.html', context)