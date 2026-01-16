from django.db import models

# Create your models here.
class Job(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(default=None, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)