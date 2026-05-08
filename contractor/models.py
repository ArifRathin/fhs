from django.db import models
from uuid import uuid4
import os

# Create your models here.

def saveWorkerPhoto(instance, filename):
    extension = filename.split('.')[-1]
    if instance.pk:
        imageName = f'{instance.pk}_{uuid4().hex}.{extension}'
    else:
        imageName = f'{uuid4().hex}.{extension}'
    
    return os.path.join('worker_images', imageName)


class Worker(models.Model):
    name = models.CharField(max_length=255)
    trade_name = models.CharField(max_length=255)
    address = models.TextField()
    post_code = models.CharField(max_length=12)
    region = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, unique=True)
    contact_no1 = models.CharField(max_length=20)
    contact_no2 = models.CharField(max_length=20, default=None, null=True)
    ethnicity = models.CharField(max_length=30, default=None, null=True)
    reliability_max = models.DecimalField(max_digits=4, decimal_places=2, default=None, null=True)
    travel_radius = models.DecimalField(max_digits=7, decimal_places=2, default=None, null=True)
    vehicle = models.BooleanField(default=False)
    out_of_hour = models.BooleanField(default=False)
    note = models.TextField(default=None, null=True)
    rates = models.DecimalField(max_digits=5, decimal_places=2)
    specialities = models.TextField(default=None, null=True)
    insurance = models.BooleanField(default=False)
    expiry_date = models.DateField(default=None, null=True)
    photo = models.ImageField(upload_to=saveWorkerPhoto, default=None, null=True)
    created_at = models.DateTimeField(auto_now_add=True)


class WorkerHistory(models.Model):
    worker = models.ForeignKey(Worker, on_delete=models.CASCADE)
    job_number = models.CharField(max_length=10, default=None, null=True)
    po_number = models.CharField(max_length=255, default=None, null=True)
    ref = models.CharField(max_length=20, default=None, null=True)
    charge = models.DecimalField(max_digits=10, decimal_places=2, default=None, null=True)
    date_completed = models.DateTimeField()
    signed_by = models.CharField(max_length=100, default=None, null=True)
    note = models.TextField(default=None, null=True)