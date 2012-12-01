from django.contrib.auth.models import User
from django.db import models

from django_countries import CountryField


gender_choices = [
    ("M", "Male"),
    ("F", "Female"),
    ]

class UserProfile(models.Model):
    user = models.ForeignKey(User, unique=True)
    #avatar =
        
    address_1 = models.CharField(max_length=80, null=True, blank=True)
    address_2 = models.CharField(max_length=80, null=True, blank=True)
    postal_code = models.PositiveIntegerField()
    city = models.CharField(max_length=80)
    country = CountryField()

    gender = models.CharField(max_length=2, choices=gender_choices, default="M")
    
    birth_day = models.DateField()
    phone_number = models.CharField(max_length=15, blank=True, default='')
    receive_newsletter = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = 'user profile'
        verbose_name_plural = 'user profiles'
        ordering = ['user__first_name', 'user__last_name',]

    def __unicode__(self):
        return self.user
