from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from account.models import User
from .models import ReportStatus, PriorityLevel, TimeUnit, FaultReport, FaultReportImage, CompletionImage
from job.models import Job
from account.models import User
from front_page.models import FrontPage
from notification.models import Notification
from django.db import transaction
from django.utils import timezone
from datetime import timedelta
from django.contrib import messages
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from fhs.image_processor import processImage
from address.models import Location
import sys
import os
# Create your views here.
def createFaultReport(request):
    if request.method == 'POST':
        contactName = request.POST.get('contact-name').strip()
        if contactName == '':
            messages.error(request, "Contact name is mandatory!", extra_tags='error-create-report')
            return redirect(request.META['HTTP_REFERER'])
        contactPhone = request.POST.get('contact-phone').strip()
        if contactPhone == '':
            messages.error(request, "Contact phone is mandatory!", extra_tags='error-create-report')
            return redirect(request.META['HTTP_REFERER'])
        if request.user.is_authenticated:
            contactEmail = request.user.email
        else:
            contactEmail = request.POST.get('contact-email').strip()
            if contactEmail == '':
                messages.error(request, "Contact email is mandatory!", extra_tags='error-create-report')
                return redirect(request.META['HTTP_REFERER'])
        description = request.POST.get('description').strip()
        if description == '':
            messages.error(request, "Description is mandatory!", extra_tags='error-create-report')
            return redirect(request.META['HTTP_REFERER'])
        images = request.FILES.getlist('images')
        location = request.POST.get('location-id').strip()
        address = request.POST.get('address').strip()
        if address == '':
            messages.error(request, "Address is mandatory!", extra_tags='error-create-report')
            return redirect(request.META['HTTP_REFERER'])
        jobId = request.POST.get('job-type')
        jobDescription = request.POST.get('job-type-text').strip()
        priorityLevel = request.POST.get('priority-level')
        if priorityLevel not in PriorityLevel:
            messages.error(request, "Priority level is invalid!", extra_tags='error-create-report')
            return redirect(request.META['HTTP_REFERER'])
        preferredTime = request.POST.get('preferred-time').strip()
        if preferredTime == '':
            messages.error(request, "Preferred time is mandatory!", extra_tags='error-create-report')
            return redirect(request.META['HTTP_REFERER'])
        poNumber = request.POST.get('po-number').strip()
        ifRecall = request.POST.get('if-recall').strip()
        if ifRecall == '1':
            ifRecall= True
        else:
            ifRecall = False
        try:
            with transaction.atomic():
                faultReport = FaultReport.objects.create(contact_name = contactName, contact_phone=contactPhone, contact_email=contactEmail, description=description, location_id=location, address=address, job_id=jobId, job_description=jobDescription, priority_level=priorityLevel, preferred_time=preferredTime)
                faultId = str(faultReport.id)
                jobNumber = 'FH1'
                for _ in range(0, (7-len(faultId))):
                    jobNumber += '0'
                jobNumber += faultId
                faultReport.job_number = jobNumber
                faultReport.po_number = poNumber
                faultReport.if_recall = ifRecall
                faultReport.save()
                
                if request.user.is_authenticated:
                    faultReport.user_technician.set([request.user.id])
                elif User.objects.filter(email=contactEmail).exists():
                    userRow = User.objects.get(email=contactEmail)
                    faultReport.user_technician.set([userRow.id])
                imageArr = []
                for image in images:
                    processedImage = processImage(image)
                    imageArr.append(FaultReportImage(fault_report = faultReport, image=processedImage))
                if imageArr:
                    FaultReportImage.objects.bulk_create(imageArr)
                admins = User.objects.filter(is_admin=True)
                notifById = None
                if request.user.is_authenticated:
                    notifById=request.user.id
                notifArr = []
                for admin in admins:
                    notification = Notification(text="A new fault report has been submitted.",notif_by_id=notifById,notif_for_id=admin.id,notif_area='F',fault_report=faultReport)
                    notifArr.append(notification)
                Notification.objects.bulk_create(notifArr)
                for notification in notifArr:
                    async_to_sync(get_channel_layer().group_send)(
                        f'user__{notification.notif_for_id}',
                        {
                            'type':'send_notification',
                            'message':{
                                'id':notification.id,
                                'text':notification.text,
                                'notif_for_id':notification.notif_for_id,
                                'notif_area':notification.notif_area,
                                'job_number':str(notification.fault_report.job_number),
                                'is_opened':notification.is_opened,
                                'is_admin':1
                            }
                        }
                    )
                messages.success(request, 'Successfully created fault report.', extra_tags='success-create-report')
                if request.user.is_authenticated:
                    return redirect('home')
                else:
                    return redirect(request.META['HTTP_REFERER'])
            messages.error(request, 'Could not create fault report.', extra_tags='error-create-report')
            return redirect(request.META['HTTP_REFERER'])
        except Exception as e:
            messages.error(request, "Something went wrong!", extra_tags='error-create-report')
            return redirect(request.META['HTTP_REFERER'])
    
    jobs = Job.objects.all()
    priorityLevels = PriorityLevel.choices
    locations = Location.objects.filter(is_active=True)
    page_ = 'Report A Fault'
    frontPage = FrontPage.objects.all().first()
    data = {
        'jobs':jobs,
        'page_':page_,
        'priority_levels':priorityLevels,
        'locations':locations,
        'front_page':frontPage
    }
    return render(request, 'front-end/submit-fault-report.html', data)


@login_required(login_url='login-user')
def faultReportList(request):
    notifications = Notification.objects.filter(is_opened=False, notif_for_id=request.user.id).order_by('-id')
    if request.user.is_admin == True and request.user.has_perm('fault_report.view_faultreport'):
        faults = FaultReport.objects.all().order_by('-created_at')
    else:
        faults = request.user.fault_report.all().order_by('-created_at')
    priorityLevels = PriorityLevel.choices
    statuses = ReportStatus.choices
    page_ = 'Fault Reports'
    sub_menu = 'Fault-Reports'
    data={
        'notifications':notifications,
        'faults':faults,
        'priority_levels':priorityLevels,
        'statuses':statuses,
        'page_':page_,
        'sub_menu':sub_menu,
        'filter_time_type':'all',
        'priority_level':'all',
        'priority_level_name':'All Priorities',
        'status':'All',
        'status_name':'All Status',
        'start_date':'all',
        'end_date':'all'
    }
    return render(request, 'front-end/admin/fault-reports.html', data)


@login_required(login_url='login-user')
def faultReportsFilter(request, status='All', priorityLevel='all', filterTimeType='all', startDate='all', endDate='all'):
    if request.method == 'POST':
        status = request.POST.get('status')
        priorityLevel = request.POST.get('priority-level')
        filterTimeType = request.POST.get('filter-time-type')
        startDate = request.POST.get('start-date')
        endDate = request.POST.get('end-date')

    notifications = Notification.objects.filter(is_opened=False, notif_for_id=request.user.id).order_by('-id')
    if filterTimeType == 'all':
        if status == 'All':
            if priorityLevel == 'all':
                if request.user.is_admin and request.user.has_perm('fault_report.view_faultreport'):
                    faultReports = FaultReport.objects.all().order_by('-created_at')
                else :
                    faultReports = request.user.fault_report.all().order_by('-created_at')
            else:
                if request.user.is_admin and request.user.has_perm('fault_report.view_faultreport'):
                    faultReports = FaultReport.objects.filter(priority_level=priorityLevel).order_by('-created_at')
                else :
                    faultReports = request.user.fault_report.filter(priority_level=priorityLevel).order_by('-created_at')
        elif status == 'Cot':
            if priorityLevel == 'all':
                if request.user.is_admin and request.user.has_perm('fault_report.view_faultreport'):
                    faultReports = FaultReport.objects.filter(status=ReportStatus.COMPLETED, is_late=False).order_by('-created_at')
                else :
                    faultReports = request.user.fault_report.filter(status=ReportStatus.COMPLETED, is_late=False).order_by('-created_at')
            else:
                if request.user.is_admin and request.user.has_perm('fault_report.view_faultreport'):
                    faultReports = FaultReport.objects.filter(status=ReportStatus.COMPLETED, priority_level=priorityLevel, is_late=False).order_by('-created_at')
                else :
                    faultReports = request.user.fault_report.filter(status=ReportStatus.COMPLETED, priority_level=priorityLevel, is_late=False).order_by('-created_at')
        else:
            if priorityLevel == 'all':
                if request.user.is_admin and request.user.has_perm('fault_report.view_faultreport'):
                    faultReports = FaultReport.objects.filter(status=status).order_by('-created_at')
                else:
                    faultReports = request.user.fault_report.filter(status=status).order_by('-created_at')
            else:
                if request.user.is_admin and request.user.has_perm('fault_report.view_faultreport'):
                    faultReports = FaultReport.objects.filter(status=status, priority_level=priorityLevel).order_by('-created_at')
                else:
                    faultReports = request.user.fault_report.filter(status=status, priority_level=priorityLevel).order_by('-created_at')
    elif filterTimeType == 'date':
        if status == 'All':
            if priorityLevel == 'all':
                if request.user.is_admin and request.user.has_perm('fault_report.view_faultreport'):
                    faultReports = FaultReport.objects.filter(created_at__gte=startDate, created_at__lte=endDate).order_by('-created_at')
                else:
                    faultReports = request.user.fault_report.filter(created_at__gte=startDate, created_at__lte=endDate).order_by('-created_at')
            else:
                if request.user.is_admin and request.user.has_perm('fault_report.view_faultreport'):
                    faultReports = FaultReport.objects.filter(created_at__gte=startDate, created_at__lte=endDate, priority_level=priorityLevel).order_by('-created_at')
                else:
                    faultReports = request.user.fault_report.filter(created_at__gte=startDate, created_at__lte=endDate, priority_level=priorityLevel).order_by('-created_at')
        elif status == 'Cot':
            if priorityLevel == 'all':
                if request.user.is_admin and request.user.has_perm('fault_report.view_faultreport'):
                    faultReports = FaultReport.objects.filter(created_at__gte=startDate, created_at__lte=endDate, status=ReportStatus.COMPLETED, priority_level=priorityLevel, is_late=False).order_by('-created_at')
                else:
                    faultReports = request.user.fault_report.filter(created_at__gte=startDate, created_at__lte=endDate, status=ReportStatus.COMPLETED, priority_level=priorityLevel, is_late=False).order_by('-created_at')
            else:
                if request.user.is_admin and request.user.has_perm('fault_report.view_faultreport'):
                    faultReports = FaultReport.objects.filter(created_at__gte=startDate, created_at__lte=endDate, status=ReportStatus.COMPLETED, priority_level=priorityLevel, is_late=False).order_by('-created_at')
                else:
                    faultReports = request.user.fault_report.filter(created_at__gte=startDate, created_at__lte=endDate, status=ReportStatus.COMPLETED, priority_level=priorityLevel, is_late=False).order_by('-created_at')
        else:
            if priorityLevel == 'all':
                if request.user.is_admin and request.user.has_perm('fault_report.view_faultreport'):
                    faultReports = FaultReport.objects.filter(created_at__gte=startDate, created_at__lte=endDate, status=status, priority_level=priorityLevel).order_by('-created_at')
                else:
                    faultReports = request.user.fault_report.filter(created_at__gte=startDate, created_at__lte=endDate, status=status, priority_level=priorityLevel).order_by('-created_at')
            else:
                if request.user.is_admin and request.user.has_perm('fault_report.view_faultreport'):
                    faultReports = FaultReport.objects.filter(created_at__gte=startDate, created_at__lte=endDate, status=status, priority_level=priorityLevel).order_by('-created_at')
                else:
                    faultReports = request.user.fault_report.filter(created_at__gte=startDate, created_at__lte=endDate, status=status, priority_level=priorityLevel).order_by('-created_at')
    else:
        if filterTimeType == '1':
            timeDiff = 1
        elif filterTimeType == '7':
            timeDiff = 7
        elif filterTimeType == '30':
            timeDiff = 30
        elif filterTimeType == '365':
            timeDiff = 365
        daysAgo = timezone.now()-timedelta(days=timeDiff)
        if status == 'All':
            if priorityLevel == 'all':
                if request.user.is_admin and request.user.has_perm('fault_report.view_faultreport'):
                    faultReports = FaultReport.objects.filter(created_at__gte=daysAgo).order_by('-created_at')
                else:
                    faultReports = request.user.fault_report.filter(created_at__gte=daysAgo).order_by('-created_at')
            else:
                if request.user.is_admin and request.user.has_perm('fault_report.view_faultreport'):
                    faultReports = FaultReport.objects.filter(created_at__gte=daysAgo, priority_level=priorityLevel).order_by('-created_at')
                else:
                    faultReports = request.user.fault_report.filter(created_at__gte=daysAgo, priority_level=priorityLevel).order_by('-created_at')
        elif status == 'Cot':
            if priorityLevel == 'all':
                if request.user.is_admin and request.user.has_perm('fault_report.view_faultreport'):
                    faultReports = FaultReport.objects.filter(created_at__gte=daysAgo, status=ReportStatus.COMPLETED, is_late=False).order_by('-created_at')
                else:
                    faultReports = request.user.fault_report.filter(created_at__gte=daysAgo, status=ReportStatus.COMPLETED, is_late=False).order_by('-created_at')
            else:
                if request.user.is_admin and request.user.has_perm('fault_report.view_faultreport'):
                    faultReports = FaultReport.objects.filter(created_at__gte=daysAgo, status=ReportStatus.COMPLETED, priority_level=priorityLevel, is_late=False).order_by('-created_at')
                else:
                    faultReports = request.user.fault_report.filter(created_at__gte=daysAgo, status=ReportStatus.COMPLETED, priority_level=priorityLevel, is_late=False).order_by('-created_at')
        else:
            if priorityLevel == 'all':
                if request.user.is_admin and request.user.has_perm('fault_report.view_faultreport'):
                    faultReports = FaultReport.objects.filter(created_at__gte=daysAgo, status=status).order_by('-created_at')
                else:
                    faultReports = request.user.fault_report.filter(created_at__gte=daysAgo, status=status).order_by('-created_at')
            else:
                if request.user.is_admin and request.user.has_perm('fault_report.view_faultreport'):
                    faultReports = FaultReport.objects.filter(created_at__gte=daysAgo, priority_level=priorityLevel, status=status).order_by('-created_at')
                else:
                    faultReports = request.user.fault_report.filter(created_at__gte=daysAgo, priority_level=priorityLevel, status=status).order_by('-created_at')
    priorityLevels = PriorityLevel.choices 
    priorityLevelName = 'All Priorities'
    if priorityLevel != 'all':
        priorityLevelName = PriorityLevel(priorityLevel).label
    statuses = ReportStatus.choices
    statusName = 'All Status'
    if status == 'Cot':
        statusName = 'Completed on time'
    elif status != 'All':
        statusName = ReportStatus(status).label
    data={
        'notifications':notifications,
        'faults':faultReports,
        'priority_levels':priorityLevels,
        'statuses':statuses,
        'page_':'Fault Reports',
        'sub_menu':'Fault-Reports',
        'status':status,
        'priority_level':priorityLevel,
        'filter_time_type':filterTimeType,
        'status_name': statusName,
        'priority_level_name':priorityLevelName,
        'start_date':startDate,
        'end_date':endDate
    }

    return render(request, 'front-end/admin/fault-reports.html', data)


@login_required(login_url='login-user')
def editFaultReport(request, faultReportId=0):
    if request.method == 'POST':
        faultReportId = request.POST.get('fault-report-id').strip()
        contactName = request.POST.get('contact-name').strip()
        if contactName == '':
            messages.error(request, 'Contact name is mandatory!', extra_tags='error-edit-report')
            return redirect(request.META['HTTP_REFERER'])
        contactPhone = request.POST.get('contact-phone').strip()
        if contactPhone == '':
            messages.error(request, 'Contact phone is mandatory!', extra_tags='error-edit-report')
            return redirect(request.META['HTTP_REFERER'])
        contactEmail = request.POST.get('contact-email').strip()
        if contactEmail == '':
            messages.error(request, 'Contact email is mandatory!', extra_tags='error-edit-report')
            return redirect(request.META['HTTP_REFERER'])
        address = request.POST.get('address').strip()
        if address == '':
            messages.error(request, "Address is mandatory!", extra_tags='error-edit-report')
            return redirect(request.META['HTTP_REFERER'])
        preferredTime = request.POST.get('preferred-time').strip()
        if preferredTime == '':
            messages.error(request, "Preferred time is mandatory!", extra_tags='error-edit-report')
            return redirect(request.META['HTTP_REFERER'])
        description = request.POST.get('description').strip()
        if description == '':
            messages.error(request, 'Description is mandatory!', extra_tags='error-edit-report')
            return redirect(request.META['HTTP_REFERER'])
        deadline = request.POST.get('deadline').strip()
        try:
            deadline = int(deadline)
            if deadline <= 0:
                messages.error(request, 'Deadline has to be at least 1', extra_tags='error-edit-report')
                return redirect(request.META['HTTP_REFERER'])
        except Exception as e:
            messages.error(request, 'Deadline is invalid!', extra_tags='error-edit-report')
            return redirect(request.META['HTTP_REFERER'])
        deadlineTimeUnit = request.POST.get('deadline-time-unit').strip()
        if deadlineTimeUnit not in TimeUnit:
            messages.error(request, 'Deadline time unit is invalid!', extra_tags='error-edit-report')
            return redirect(request.META['HTTP_REFERER'])
        completionImages = request.FILES.getlist('completion-image')
        note = request.POST.get('note').strip()
        poNumber = request.POST.get('po-number').strip()
        ifRecall = request.POST.get('if-recall').strip()
        if ifRecall == '1':
            ifRecall = True
        else:
            ifRecall = False
    faultReport = FaultReport.objects.filter(id=faultReportId).first()
    if not faultReport:
        messages.error(request, 'Report does not exist!', extra_tags='error-edit-report')
        return redirect(request.META['HTTP_REFERER'])
    if request.method == 'GET':
        statuses = ReportStatus.choices
        priorityLevels = PriorityLevel.choices
        timeUnits = TimeUnit.choices
        technicians = User.objects.filter(is_technician=True, is_available=True)
        deadline = None
        daysTaken = None
        hoursTaken = None
        minutesTaken = None
        secondsTaken = None
        assessment = None
        if faultReport.started_at != None:
            deadline = faultReport.started_at + timedelta(hours=2)
        if faultReport.completed_at != None:
            timeDiff = faultReport.completed_at - faultReport.started_at
            secondsTaken = int(timeDiff.total_seconds())
            daysTaken = secondsTaken//86400
            remSeconds = secondsTaken%86400
            hoursTaken = remSeconds//3600
            remSeconds = remSeconds%3600
            minutesTaken = remSeconds//60
            secondsTaken = remSeconds%60
            
            if faultReport.deadline_time_unit == 'H':
                secondsDeadline = faultReport.deadline * 3600
            elif faultReport.deadline_time_unit == 'D':
                secondsDeadline = faultReport.deadline * 86400
            if int(timeDiff.total_seconds()) <= secondsDeadline:
                assessment = 'Completed on time'
            else:
                lateInSeconds = int(timeDiff.total_seconds()) - secondsDeadline
                lateInDays = lateInSeconds//86400
                remSeconds = lateInSeconds%86400
                lateInHours = remSeconds//3600
                remSeconds = remSeconds%3600
                lateInMins = remSeconds//60
                lateInSecs = remSeconds%60
                assessment = f'{lateInDays} day(s) {lateInHours} hour(s) {lateInMins} min(s) {lateInSecs} second(s) Late'
        notifications = Notification.objects.filter(is_opened=False, notif_for_id=request.user.id).order_by('-id')
        locations = Location.objects.filter(is_active=True)
        page_ = 'Update Fault Report'
        sub_menu = 'Fault-Reports'
        data = {
            'notifications':notifications,
            'page_':page_,
            'sub_menu':sub_menu,
            'fault':faultReport,
            'locations':locations,
            'statuses':statuses,
            'priority_levels':priorityLevels,
            'time_units':timeUnits,
            'technicians':technicians,
            'deadline':deadline,
            'days_taken':daysTaken,
            'hours_taken':hoursTaken,
            'minutes_taken':minutesTaken,
            'seconds_taken':secondsTaken,
            'assessment':assessment
        }
        return render(request, 'front-end/admin/edit-fault-report.html', data)
    faultReport.po_number = poNumber
    faultReport.if_recall = ifRecall
    faultReport.contact_name = contactName
    faultReport.contact_phone = contactPhone
    faultReport.contact_email = contactEmail
    faultReport.address = address
    faultReport.preferred_time = preferredTime
    faultReport.description = description
    faultReport.note = note
    faultReport.deadline = deadline
    faultReport.deadline_time_unit = deadlineTimeUnit
    try:
        with transaction.atomic():
            imgArr = []
            for image in completionImages:
                image = processImage(image)
                imgArr.append(CompletionImage(fault_report=faultReport, image=image))
            if imgArr:
                CompletionImage.objects.bulk_create(imgArr)
            faultReport.save()
            messages.success(request, 'Successfully edited the report.', extra_tags='success-edit-report')
    except:
        messages.error(request, 'Something went wrong!', extra_tags='error-edit-report')
    return redirect(request.META['HTTP_REFERER'])


@login_required(login_url='login-user')
def deleteFaultReport(request, reportId):
    if request.user.is_admin and request.user.has_perm('fault_report.delete_faultreport'):
        try:
            with transaction.atomic():
                faultReport = FaultReport.objects.filter(id=reportId).first()
                faultReportImages = FaultReportImage.objects.filter(fault_report_id=faultReport.id)
                for image in faultReportImages:
                    image.image.delete(save=False)
                    image.delete()
                faultReport.delete()
                messages.success(request, 'Successfully deleted report', extra_tags='success-fault-report')
                return redirect(request.META['HTTP_REFERER'])
        except Exception as e:
            messages.error(request, 'Failed to delete report!', extra_tags='error-fault-report')
            return redirect(request.META['HTTP_REFERER'])
    else:
        messages.error(request, 'You are not permitted to delete this report!', extra_tags='error-fault-report')
        return redirect(request.META['HTTP_REFERER'])


@login_required(login_url='login-user')
def assignATechnician(request):
    try:
        with transaction.atomic():
            technicianId = request.POST.get('technician-id')
            jobNumber = request.POST.get('job-number')

            faultReport = FaultReport.objects.get(job_number=jobNumber)
            userArr = []
            users = faultReport.user_technician.all()
            for user in users:
                if user.is_technician == False:
                    userArr.append(user.id)
            userArr.append(technicianId)
            faultReport.user_technician.set(userArr)
            faultReport.is_assigned = True

            technician = User.objects.get(id=technicianId)
            # technician.is_available = False
            technician.save()

            if faultReport.status == 'S' or faultReport.status == 'QS' or faultReport.status == 'QA':
                faultReport.status = 'A'
            notifArr = []
            for user in faultReport.user_technician.all():
                if user.is_technician:
                    notification = Notification(text="You have been assigned a new task.",notif_by_id=request.user.id,notif_for_id=user.id,notif_area='A',fault_report=faultReport)
                elif user.is_enduser:
                    notification = Notification(text="A technician has been assigned to your task.",notif_by_id=request.user.id,notif_for_id=user.id,notif_area='A',fault_report=faultReport)
                notifArr.append(notification)
            Notification.objects.bulk_create(notifArr)
            for notification in notifArr:
                    async_to_sync(get_channel_layer().group_send)(
                        f'user__{notification.notif_for_id}',
                        {
                            'type':'send_notification',
                            'message':{
                                'id':notification.id,
                                'text':notification.text,
                                'notif_for_id':notification.notif_for_id,
                                'notif_area':notification.notif_area,
                                'job_number':str(notification.fault_report.job_number),
                                'is_opened':notification.is_opened,
                                'is_admin':0
                            }
                        }
                    )
            faultReport.save()
            messages.success(request, 'Technician successfully assigned.', extra_tags='success-edit-report')
    except Exception as e:
        messages.error(request, str(e), extra_tags='error-edit-report')
    return redirect(request.META['HTTP_REFERER'])
    

@login_required(login_url='login-user')
def startTask(request, jobNumber):
    faultReport = FaultReport.objects.get(job_number=jobNumber)
    if faultReport.is_assigned == True:
        faultReport.started_at = timezone.now()
        faultReport.status = 'IP'
        try:
            faultReport.save()
            messages.success(request, 'The task has been started', extra_tags='success-edit-report')
        except:
            messages.error(request, 'Something went wrong!', extra_tags='error-edit-report')
    else:
        messages.error(request, 'The task has to be assigned to a technician first!')
    return redirect(request.META['HTTP_REFERER'])


@login_required(login_url='login-user')
def pauseTask(request, jobNumber):
    faultReport = FaultReport.objects.get(job_number=jobNumber)
    if faultReport.status == 'IP':
        faultReport.status = 'P'
        try:
            faultReport.save()
            messages.success(request, 'The task has been paused.', extra_tags='success-edit-report')
        except:
            messages.error(request, 'Something went wrong!', extra_tags='error-edit-report')
    else:
        messages.error(request, 'The task cannot be paused.', extra_tags='error-edit-report')
    return redirect(request.META['HTTP_REFERER'])


@login_required(login_url='login-user')
def resumeTask(request, jobNumber):
    faultReport = FaultReport.objects.get(job_number=jobNumber)
    if faultReport.status == 'P':
        faultReport.status = 'IP'
        try:
            faultReport.save()
            messages.success(request, 'The task has been resumed.', extra_tags='success-edit-report')
        except:
            messages.error(request, 'Something went wrong!', extra_tags='error-edit-report')
    else:
        messages.error(request, 'Failed to resume task!', extra_tags='error-edit-report')
    return redirect(request.META['HTTP_REFERER'])


@login_required(login_url='login-user')
def completeTask(request, jobNumber):
    if FaultReport.objects.filter(job_number=jobNumber).exists():
        faultReport = FaultReport.objects.get(job_number=jobNumber)
    else:
        messages.error(request, 'Report does not exist!', extra_tags='error-edit-report')
        return redirect(request.META['HTTP_REFERER'])
    try:
        with transaction.atomic():
            faultReport.completed_at = timezone.now()
            faultReport.save()

            timeTaken = faultReport.completed_at - faultReport.started_at
            faultReport.completion_time = timeTaken.total_seconds()

            if faultReport.deadline_time_unit == 'H':
                secondsDeadline = faultReport.deadline * 3600
            elif faultReport.deadline_time_unit == 'D':
                secondsDeadline = faultReport.deadline * 86400
            if timeTaken.total_seconds() <= secondsDeadline:
                faultReport.is_late = False
            else:
                faultReport.is_late = True

            users = faultReport.user_technician.all()

            technicianId = 0
            for user in users:
                if user.is_technician == True:
                    technicianId = user.id
                    user.save()

            faultReport.status = 'C'
            faultReport.save()

            notifForIds = []
            if User.objects.filter(email=faultReport.contact_email).exists():
                customer = User.objects.get(email=faultReport.contact_email)
                customerId = customer.id
                notifForIds.append(customerId)
            notifForIds.append(technicianId)

            notifArr = []
            for id in notifForIds:
                notification = Notification(text="Task completed",notif_by_id=request.user.id,notif_for_id=id,notif_area='F',fault_report=faultReport)
                notifArr.append(notification)
            Notification.objects.bulk_create(notifArr)
            for notification in notifArr:
                    async_to_sync(get_channel_layer().group_send)(
                        f'user__{notification.notif_for_id}',
                        {
                            'type':'send_notification',
                            'message':{
                                'id':notification.id,
                                'text':notification.text,
                                'notif_for_id':notification.notif_for_id,
                                'notif_area':notification.notif_area,
                                'job_number':str(notification.fault_report.job_number),
                                'is_opened':notification.is_opened,
                                'is_admin':0
                            }
                        }
                    )
            messages.success(request, 'The task has been completed.', extra_tags='success-edit-report')
    except:
        messages.error(request, 'Something went wrong!', extra_tags='error-edit-report')

    return redirect(request.META['HTTP_REFERER'])
    

def faultReportDetails(request, jobNumber):
    faultReport = FaultReport.objects.get(job_number=jobNumber)
    deadline = faultReport.deadline
    deadline_time_unit = faultReport.deadline_time_unit
    daysTaken = None
    hoursTaken = None
    minutesTaken = None
    secondsTaken = None
    assessment = None
    if faultReport.started_at != None:
        if deadline_time_unit == 'H':
            deadline = faultReport.started_at + timedelta(hours=deadline)
        elif deadline_time_unit == 'D':
            deadline = faultReport.started_at + timedelta(days=deadline)
    if faultReport.completed_at != None:
        timeDiff = faultReport.completed_at - faultReport.started_at
        secondsTaken = int(timeDiff.total_seconds())
        daysTaken = secondsTaken//86400
        remSeconds = secondsTaken%86400
        hoursTaken = remSeconds//3600
        remSeconds = remSeconds%3600
        minutesTaken = remSeconds//60
        secondsTaken = remSeconds%60
        
        if faultReport.deadline_time_unit == 'H':
            secondsDeadline = faultReport.deadline * 3600
        elif faultReport.deadline_time_unit == 'D':
            secondsDeadline = faultReport.deadline * 86400
        if int(timeDiff.total_seconds()) <= secondsDeadline:
            assessment = 'Completed on time'
        else:
            lateInSeconds = int(timeDiff.total_seconds()) - secondsDeadline
            lateInDays = lateInSeconds//86400
            remSeconds = lateInSeconds%86400
            lateInHours = remSeconds//3600
            remSeconds = remSeconds%3600
            lateInMins = remSeconds//60
            lateInSecs = remSeconds%60
            assessment = f'{lateInDays} day(s) {lateInHours} hour(s) {lateInMins} min(s) {lateInSecs} second(s) Late'
    notifications = Notification.objects.filter(is_opened=False, notif_for_id=request.user.id).order_by('-id')
    priorityLevels = PriorityLevel.choices
    statuses = ReportStatus.choices
    page_ = 'Report Details'
    sub_menu = 'Fault-Reports'
    data = {
        'notifications':notifications,
        'fault_report' : faultReport,
        'page_':page_,
        'sub_menu':sub_menu,
        'deadline': deadline,
        'days_taken': daysTaken,
        'minutes_taken': minutesTaken,
        'hours_taken': hoursTaken,
        'seconds_taken': secondsTaken,
        'assessment': assessment,
        'priority_levels': priorityLevels,
        'statuses': statuses
    }
    if request.user.is_authenticated:
        return render(request, 'front-end/view-fault-report.html', data)
    else:
        front_page = FrontPage.objects.all().first()
        data['front_page'] = front_page
        return render(request, 'front-end/closure-summary.html', data)