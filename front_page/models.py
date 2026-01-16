from django.db import models
import uuid
import os
from account.models import User

# Create your models here.
def saveFrontImage(instance, filename):
    filename = filename.split('.')
    extension = filename[-1]
    if instance.pk:
        imageName = f'{instance.pk}_{uuid.uuid4().hex}.{extension}'
    else:
        imageName = f'_{uuid.uuid4().hex}.{extension}'
    return os.path.join('front_page', imageName)


def saveMemberImage(instance, filename):
    filename = filename.split('.')
    extension = filename[-1]
    if instance.pk:
        imageName = f'{instance.pk}_{uuid.uuid4().hex}.{extension}'
    else:
        imageName = f'_{uuid.uuid4().hex}.{extension}'
    return os.path.join('front_page', imageName)


class FrontPage(models.Model):
    logo = models.ImageField(upload_to=saveFrontImage)
    banner_image = models.ImageField(upload_to=saveFrontImage)
    contact_email = models.CharField(max_length=255)
    contact_phone = models.CharField(max_length=255)
    contact_address = models.TextField(default=None, null=True)
    about_us = models.TextField(default=None, null=True)
    last_updated_at = models.DateTimeField(auto_now=True)


class CustomerReview(models.Model):
    customer = models.ForeignKey(User, default=None, null=True, on_delete=models.CASCADE)
    customer_name = models.CharField(max_length=255)
    review = models.TextField()
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)


class Team(models.Model):
    member = models.ForeignKey(User, related_name='member', default=None, null=True, on_delete=models.CASCADE)
    member_image = models.ImageField(upload_to=saveMemberImage, default='front_page/default_profile.png')
    designation = models.CharField(max_length=50, default=None, null=True)
    details = models.TextField(default=None, null=True)
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)