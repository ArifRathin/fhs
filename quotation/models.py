from django.db import models
from account.models import User
from fault_report.models import FaultReport
from django.db.models.signals import post_save
from django.dispatch import receiver
from fhs import email_sender
from django.urls import reverse
from django.conf import settings
# Create your models here.


class PaymentStatus(models.TextChoices):
    PAID = 'P', 'Paid',
    UNPAID = 'U', 'Unpaid'


class ApprovalStatus(models.TextChoices):
    APPROVED = 'QA', 'Approved',
    PENDING = 'QP', 'Pending Approval',
    DISAPPROVED = 'QD', 'Disapproved',
    CANCELLED = 'QC', 'Cancelled'


class Quotation(models.Model):
    fault_report = models.ForeignKey(FaultReport, on_delete=models.CASCADE, related_name='quotes')
    quote_ref_num = models.CharField(max_length=20, default=None, null=True)
    payment_status = models.CharField(choices=PaymentStatus.choices, default=PaymentStatus.UNPAID, max_length=1)
    sub_total_bill = models.FloatField(default=0)
    total_bill = models.FloatField(default=0)
    sales_tax = models.FloatField(default=0)
    approval_status = models.CharField(ApprovalStatus, choices=ApprovalStatus.choices, default=ApprovalStatus.PENDING)
    is_sent = models.BooleanField(default=False)
    email_code = models.CharField(max_length=100, default=None, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

class Bill(models.Model):
    quotation = models.ForeignKey(Quotation, on_delete=models.CASCADE, related_name='bills')
    service_name = models.CharField(max_length=255)
    price_per_unit = models.FloatField()
    total_units = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)


@receiver(post_save, sender=Quotation)
def sendEmail(sender, instance, created, **kwargs):
    if instance.fault_report.status == 'QS':
        subject = 'New Quotation Created'
        to = []
        to.append(instance.fault_report.contact_email)
        body='front-end/emails/quotation-created.html'
        basicUrl = settings.BASIC_URL
        quoteLink = reverse('view-client-quotation', args=[instance.email_code])
        quoteFullLink = f'{basicUrl}{quoteLink}'
        print(quoteFullLink)
        context = {
            'receiver_name':instance.fault_report.contact_name,
            'quote_full_link':quoteFullLink
        }
        email_sender.sendEmail.delay(subject=subject, to=to, body=body, context=context)
    elif instance.fault_report.status == 'QA':
        subject = 'Quotation Approved'
        superAdmin = User.objects.filter(is_superadmin=True).first()
        to = []
        to.append(superAdmin.email)
        body='front-end/emails/quotation-approved.html'
        basicUrl = settings.BASIC_URL
        quoteLink = reverse('view-quotation', args=[instance.quote_ref_num])
        quoteFullLink = f'{basicUrl}{quoteLink}'
        print(quoteFullLink)
        context = {
            'quote_full_link':quoteFullLink
        }
        email_sender.sendEmail.delay(subject=subject, to=to, body=body, context=context)