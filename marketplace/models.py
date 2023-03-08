from django.db import models

from accounts.models import User
from menu.models import FoodItem

# Create your models here.
class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)    
    foodItem = models.ForeignKey(FoodItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.user.first_name
    
class Tax(models.Model):
    type = models.CharField(max_length=20, unique=True)
    percentage = models.DecimalField(decimal_places=2, max_digits=4, verbose_name="Tax Percentage(%)")
    is_active = models.BooleanField(default=False)
    
    class Meta:
        verbose_name_plural = 'Tax'
    
    def __str__(self) -> str:
        return self.type