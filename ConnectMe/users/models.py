from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.db import models
from django.conf import settings as django_settings
import datetime
import os
from django_countries.fields import CountryField
class UserProfile(models.Model):
    Gender=(('M','Male'),('F','Female'),)
    user = models.OneToOneField(User)
    address = models.CharField(max_length=140,blank=True)
    gender = models.CharField(max_length=1,choices=Gender,blank=True)
    address=models.CharField(max_length=10,blank=True)
    phone_number=models.CharField(max_length=10,blank=True)
    profile_picture = models.ImageField(blank=True)
    country = CountryField(blank=True)
    date_of_birth = models.DateField(blank=True,null=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

    def get_picture(self):
        no_picture = django_settings.STATIC_URL + 'img/user.png'
        try:
            filename    = django_settings.MEDIA_ROOT + '/profile_pictures/' + self.user.username + '.jpg'
            picture_url = django_settings.MEDIA_URL + 'profile_pictures/' + self.user.username + '.jpg'
            if os.path.isfile(filename):
                return picture_url
            else:
                return no_picture
        except Exception, e:
            return no_picture

    def get_screen_name(self):
        try:
            if self.user.get_full_name():
                return self.user.get_full_name()
            else:
                return self.user.username
        except:
            return self.user.username

    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            Profile.objects.create(user=instance)
            
    def save_user_profile(sender, instance, **kwargs):
        instance.profile.save()
        post_save.connect(create_user_profile, sender=User)
        post_save.connect(save_user_profile, sender=User)