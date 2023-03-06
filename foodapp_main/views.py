
from django.shortcuts import render
from django.http import HttpResponse
from foodapp_main.utils import get_or_set_current_location

from vendor.models import Vendor
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.measure import D # ``D`` is a shortcut for ``Distance``
from django.contrib.gis.db.models.functions import Distance


def home(request):
    
    if get_or_set_current_location(request) is not None:
        pnt = GEOSGeometry('POINT(%s %s)' %(get_or_set_current_location(request)), srid=4326)
    
        approved_vendors= Vendor.objects.filter(is_approved=True, 
                                        user__is_active=True,
                                        user_profile__location__distance_lte=(pnt, D(mi=100))
                                        ).annotate(distance=Distance("user_profile__location", pnt)).order_by("distance")[:8]
    
        for v in approved_vendors:
            v.mls = round(v.distance.mi,1)
        
    else:
        approved_vendors= approved_vendors= Vendor.objects.filter(is_approved=True, user__is_active=True)[:8]
    
    
    context = {
        'vendors' : approved_vendors
    }
    return render(request, 'home.html', context)