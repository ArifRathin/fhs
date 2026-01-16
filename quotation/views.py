from django.shortcuts import render, HttpResponse, redirect
from django.db import transaction
from .models import Quotation, Bill
from django.utils import timezone
from account.models import User
from notification.models import Notification
from front_page.models import FrontPage
import random
from django.contrib import messages
from django.contrib.auth.decorators import login_required

# Create your views here.
@login_required(login_url='login-user')
def createQuotation(request, faultReportId=0):
    if request.method == 'POST':
        faultReportId = request.POST.get('fault-report-id')
        now = timezone.now()
        formattedTime = now.strftime("%H%S%M%y%m%d")
        quoteRefNum = f'{faultReportId}{formattedTime}'
        print(quoteRefNum)
        faultReportId = request.POST.get('fault-report-id')
        descriptions = request.POST.getlist('description')
        pricePerUnit = request.POST.getlist('price-per-unit')
        totalUnits = request.POST.getlist('total-units')

        salesTax = request.POST.get('sales-tax').strip()

        subtotalBill = 0
        for i in range(len(pricePerUnit)):
            if pricePerUnit[i] != '' and totalUnits[i] != '':
                subtotalBill += (float(pricePerUnit[i])*int(totalUnits[i]))
        if salesTax != '' and salesTax != '0':
            salesTax = float(salesTax)
        else:
            salesTax = 0
        totalBill = subtotalBill + ((subtotalBill*salesTax)/100)
        print(totalBill)
        try:
            with transaction.atomic():
                quotation = Quotation.objects.create(fault_report_id = faultReportId, quote_ref_num=quoteRefNum, sub_total_bill=subtotalBill, total_bill=totalBill, sales_tax=salesTax)
                billArr = []
                for n in range(len(descriptions)):
                    if pricePerUnit[n] != '' and totalUnits[n] != '':
                        bill = Bill(quotation_id=quotation.id, service_name=descriptions[n], price_per_unit=float(pricePerUnit[n]), total_units=int(totalUnits[n]))
                        billArr.append(bill)
                if billArr:
                    Bill.objects.bulk_create(billArr)
                messages.success(request, 'Successfully created the quotation.', extra_tags='success-create-quotation')
                return redirect(request.META['HTTP_REFERER'])
            messages.error(request, 'Could not create quotation!', extra_tags='error-create-quotation')
            return redirect(request.META['HTTP_REFERER'])
        except:
            messages.error(request, 'Something went wrong!', extra_tags='error-create-quotation')
            return redirect(request.META['HTTP_REFERER'])
    data = {
        'faultReportId':faultReportId
    }
    return render(request, 'front-end/admin/create-quotation.html', data)

@login_required(login_url='login-user')
def viewQuotation(request, quoteRefNum):
    quotation = Quotation.objects.get(quote_ref_num=quoteRefNum)
    data = {
        'quotation':quotation
    }
    return render(request, 'front-end/admin/view-quotation.html', data)


def viewClientQuotation(request, quoteEmailCode):
    quotation = Quotation.objects.get(email_code=quoteEmailCode)
    frontPage = FrontPage.objects.all().first()
    data = {
        'quotation':quotation,
        'front_page':frontPage
    }

    return render(request, "front-end/view-quotation.html", data)

@login_required(login_url='login-user')
def sendQuotation(request, quoteRefNum):
    try:
        with transaction.atomic():
            quotation = Quotation.objects.get(quote_ref_num=quoteRefNum)
            # quotation.is_sent = True
            randomCharArr=['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z','a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z','0','1','2','3','4','5','6','7','8','9']
            randomStr = ''
            for _ in range(50):
                randNum = random.randint(0,61)
                pickedChar = randomCharArr[randNum]
                randomStr += pickedChar
            print(randomStr)
            randomStr += '_'+quoteRefNum
            quotation.email_code = randomStr
            quotation.is_sent = True
            quotation.fault_report.status = 'QS'
            quotation.fault_report.save()
            quotation.save()
            if User.objects.filter(email=quotation.fault_report.contact_email).exists():
                user = User.objects.get(email=quotation.fault_report.contact_email)
                Notification.objects.create(text="A quotation has been created for your request.",notif_by_id=request.user.id,notif_for_id=user.id,notif_area='Q',fault_report=quotation.fault_report,quotation=quotation)
            messages.success(request, 'Quotation sent to the client', extra_tags='success-sent-quotation')
        messages.error(request, 'Quotation could not be sent!', extra_tags='error-sent-quotation')
    except:
        messages.error(request, 'Something went wrong!', extra_tags='error-sent-quotation')
    return redirect(request.META['HTTP_REFERER'])
    

@login_required(login_url='login-user')
def cancelQuotation(request, quoteRefNum):
    try:
        quotation = Quotation.objects.get(quote_ref_num=quoteRefNum)
        quotation.approval_status = 'C'
        quotation.save()
        messages.success(request, 'Quotation cancelled.', extra_tags='success-cancel-quotation')
    except:
        messages.error(request, 'Something went wrong!', extra_tags='error-cancel-quotation')
    return redirect(request.META['HTTP_REFERER'])


def updateClientApprovalStatus(request, quoteRefNum, approvalStatus):
    try:
        with transaction.atomic():
            quotation = Quotation.objects.get(quote_ref_num=quoteRefNum)
            quotation.approval_status = approvalStatus
            quotation.is_sent = False
            quotation.fault_report.status = approvalStatus
            quotation.fault_report.save()
            quotation.save()
            notifById = None
            if User.objects.filter(email=quotation.fault_report.contact_email).exists():
                user = User.objects.get(email=quotation.fault_report.contact_email)
                quotation.fault_report.user_technician.set([user.id])
                notifById = user.id
            admins = User.objects.filter(is_admin=True).filter()
            notifArr = []
            for admin in admins:
                text = f'{quotation.fault_report.contact_name} has updated the approval status.'
                notification = Notification(text=text,notif_by_id=notifById,notif_for_id=admin.id,notif_area='Q',fault_report=quotation.fault_report,quotation=quotation)
                notifArr.append(notification)
            Notification.objects.bulk_create(notifArr) 
            messages.success(request, 'Successfully updated.', extra_tags='success-update-quotation')
            return redirect(request.META['HTTP_REFERER'])
        messages.error(request, 'Could not update!', extra_tags='error-update-quotation')
        return redirect(request.META['HTTP_REFERER'])
    except Exception as e:
        messages.error(request, 'Something went wrong!', extra_tags='error-update-quotation')
        return redirect(request.META['HTTP_REFERER'])