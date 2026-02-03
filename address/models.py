from django.db import models

# Create your models here.
class Location(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField(default=None, null=True)
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)


class Organization(models.Model):
    location = models.ManyToManyField(Location, related_name='location')
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)