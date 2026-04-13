from django.db import models
from job.models import Job
import uuid
import os

# Create your models here.
class Property(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField()
    notes = models.TextField(default=None, null=True)
    created_at = models.DateTimeField(auto_now_add=True)


class VisitingDates(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='visits')
    visiting_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)


class ItemCondition(models.TextChoices):
    OK = 'O', 'Ok'
    MONITOR = 'M', 'Monitor'
    NEEDS_REPAIR = 'NR', 'NEEDS REPAIR'


class Item(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name="items")
    name = models.CharField(max_length=255)
    notes = models.TextField(default=None, null=True)
    category = models.ForeignKey(Job, on_delete=models.SET_NULL, null=True)
    condition = models.CharField(max_length=3, choices=ItemCondition.choices, default=ItemCondition.OK)
    date_recorded = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)


def saveItemPhoto(instance, filename):
    extension = filename.split('.')[-1]
    if instance.pk:
        image = f'{instance.pk}{uuid.uuid().hex}.{extension}'
    else:
        image = f'{uuid.uuid4().hex}.{extension}'
    
    return os.path.join('property_items', image)


class ItemPhoto(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='photos')
    image = models.ImageField(upload_to=saveItemPhoto)
    created_at = models.DateTimeField(auto_now_add=True)