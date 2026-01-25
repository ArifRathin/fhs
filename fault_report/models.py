from django.db import models
from job.models import Job
from account.models import User
import uuid
import os
from django.db.models.signals import post_save
from django.dispatch import receiver
from fhs import email_sender
from django.urls import reverse
from django.conf import settings
# Create your models here.
class ReportStatus(models.TextChoices):
    SUBMITTED = 'S', 'Submitted'
    QUOTE_SENT = 'QS', 'Quote sent'
    QUOTE_APPROVED = 'QA', 'Quote approved'
    QUOTE_DISAPPROVED = 'QD', 'Quote disapproved'
    QUOTE_CANCELED = 'QC', 'Quote disapproved'
    ASSIGNED = 'A', 'Assigned',
    IN_PROGRESS = 'IP', 'In progress'
    PAUSED = 'P', 'Paused'
    COMPLETED = 'C', 'Completed'


class PriorityLevel(models.TextChoices):
    LOW = 'L', 'Low'
    MODERATE = 'M', 'Moderate',
    HIGH = 'H', 'High',
    URGENT = 'U', 'Urgent',


class TimeUnit(models.TextChoices):
    HOUR = 'H', 'Hour'
    DAY = 'D', 'Day'


class FaultReport(models.Model):
    fault_id = models.UUIDField(primary_key=False, default=uuid.uuid4, editable=True)
    user_technician = models.ManyToManyField(User, related_name='fault_report', default=None, null=True) # either a customer or a technician
    contact_name = models.CharField(max_length=255)
    contact_phone = models.CharField(max_length=20)
    contact_email = models.CharField(max_length=255)
    location = models.TextField()
    job = models.ForeignKey(Job, on_delete=models.CASCADE, default=None, null=True)
    job_description = models.CharField(max_length=255, default=None, null=True)
    priority_level = models.CharField(choices=PriorityLevel.choices, max_length=2, default=PriorityLevel.LOW)
    description = models.TextField()
    status = models.CharField(choices=ReportStatus.choices, max_length=2, default=ReportStatus.SUBMITTED)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    started_at = models.DateTimeField(default=None, null=True)
    completed_at = models.DateTimeField(default=None, null=True)
    note = models.TextField(default=None, null=True)
    deadline = models.IntegerField(default=1)
    deadline_time_unit = models.CharField(choices=TimeUnit.choices, max_length=1, default=TimeUnit.DAY)
    is_assigned = models.BooleanField(default=False)
    completion_time = models.BigIntegerField(default=0)
    is_late = models.BooleanField(default=False)


def saveFaultReportImage(instance, filename):
    filename = filename.split('.')
    extension = filename[-1]
    if instance.pk:
        image = f'{instance.pk}{uuid.uuid4().hex}.{extension}'
    else:
        image = f'{uuid.uuid4().hex}.{extension}'
    return os.path.join('fault_report_attachments', image)


class FaultReportImage(models.Model):
    fault_report = models.ForeignKey(FaultReport, on_delete=models.CASCADE)
    image = models.ImageField(upload_to=saveFaultReportImage)


@receiver(post_save, sender=FaultReport)
def sendEmail(sender, instance, created, **kwargs):
    if instance.status == 'S':
        superAdmin = User.objects.filter(is_superadmin=True).first()
        to = []
        to.append(superAdmin.email)
        subject = 'New Fault Report Submitted'
        body = 'front-end/emails/submitted-report.html'
        context = {}
        email_sender.sendEmail.delay(subject=subject, body=body, to=to, context=context)
    elif instance.status == 'C':
        to = []
        to.append(instance.contact_email)
        subject = 'Task Completed'
        body = 'front-end/emails/completed-task.html'
        detailsLink = reverse('fault-report-details', args=[instance.fault_id])
        detailsFullLink = f'{settings.BASIC_URL}{detailsLink}'
        context = {
            'receiver_name':instance.contact_name,
            'details_full_link':detailsFullLink
        }
        email_sender.sendEmail(subject=subject, body=body, to=to, context=context)
    elif instance.status == 'A':
        for user in instance.user_technician.all():
            to = []
            to.append(user.email)
            subject = 'Task Assigned'
            if user.is_enduser == True:
                body = 'front-end/emails/assigned-task-user.html'
            elif user.is_technician == True:
                body = 'front-end/emails/assigned-task-technician.html'
            detailsLink = reverse('fault-report-details', args=[instance.fault_id])
            detailsFullLink = f'{settings.BASIC_URL}{detailsLink}'
            context = {
                'receiver_name':f'{user.first_name} {user.last_name}',
                'details_full_link':detailsFullLink
            }
            email_sender.sendEmail(subject=subject, body=body, to=to, context=context)