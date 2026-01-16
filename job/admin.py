from django.contrib import admin
from .models import Job
# Register your models here.
class JobAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'is_active', 'created_at')


admin.site.register(Job, JobAdmin)