from django.db import models
from fault_report.models import FaultReport
from quotation.models import Quotation
from account.models import User
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