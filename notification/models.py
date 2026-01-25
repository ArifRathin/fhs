from django.db import models
from fault_report.models import FaultReport
from quotation.models import Quotation
from account.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
# Create your models here.

class NotifArea(models.TextChoices):
    FAULT_REPORT = 'F', 'Fault report'
    QUOTATION = 'Q', 'Quotation'
    ASSIGNMENT = 'A', 'Assignment'
    SUMMARIZE = 'S', 'Summarize'


class Notification(models.Model):
    text = models.TextField()
    notif_by_id = models.IntegerField(default=None,null=True)
    notif_for_id = models.IntegerField(default=None,null=True)
    notif_area = models.CharField(choices=NotifArea.choices, default=None, max_length=1)
    fault_report = models.ForeignKey(FaultReport, default=None, null=True, on_delete=models.CASCADE)
    quotation = models.ForeignKey(Quotation, default=None, null=True, on_delete=models.CASCADE)
    is_opened = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)


@receiver(post_save, sender=Notification)
def send_to_consumer(sender, instance, created, **kwargs):
    if created:
        channel_name = get_channel_layer()
        if instance.fault_report.status == 'QS':
            isAdmin = 0
            quoteRefNum = 0
            emailCode = instance.quotation.email_code
        elif instance.fault_report.status == 'C':
            isAdmin = 0
            quoteRefNum = 0
            emailCode = 0
        
        async_to_sync(channel_name.group_send)(
            f"user__{instance.notif_for_id}",
            {
                'type':'send_notification',
                'message':{
                    'id':instance.id,
                    'text':instance.text,
                    'notif_for_id':instance.notif_for_id,
                    'notif_area':instance.notif_area,
                    'fault_report_id':str(instance.fault_report.fault_id),
                    'quotation':instance.quotation.id,
                    'is_opened':instance.is_opened,
                    'is_admin':isAdmin,
                    'quote_ref_num':quoteRefNum,
                    'email_code':emailCode
                }
            }
        )