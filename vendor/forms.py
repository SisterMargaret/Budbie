from django import forms
from accounts.validators import allow_only_images_validator
from vendor.models import OpeningHour, Vendor


class VendorForm(forms.ModelForm):
    vendor_license = forms.FileField(widget=forms.FileInput(attrs={'class':'btn btn-info'}), validators=[allow_only_images_validator])
    class Meta:
        model = Vendor
        fields = ['vendor_name', 'vendor_license', 'vat_number']
        
class OpeningHoursForm(forms.ModelForm):
    
    class Meta:
        model=OpeningHour
        fields = ['day','from_hour','to_hour', 'is_closed']