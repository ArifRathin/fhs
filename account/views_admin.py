from django.shortcuts import render, HttpResponse, redirect
from .models import User
from notification.models import Notification
from fault_report.models import FaultReport
from front_page.models import FrontPage
from django.db.models import Q, Avg
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Permission
from django.contrib import messages
# Create your views here.
def createAdmin(request, type='external'):
    if request.method == 'POST':
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Admin already exists', extra_tags='error-create-admin')
            return redirect(request.META['HTTP_REFERER'])
        
        password = request.POST.get('password')
        if len(password) < 6:
            messages.error(request, 'Password has to be at least 6 characters!', extra_tags='error-create-admin')
            return redirect(request.META['HTTP_REFERER'])
        retypePassword = request.POST.get('retype-password')
        if password != retypePassword:
            messages.error(request, "Passwords don't match", extra_tags='error-create-admin')
            return redirect(request.META['HTTP_REFERER'])

        firstName = request.POST.get('first-name').strip()
        lastName = request.POST.get('last-name').strip()
        if firstName == '':
            firstName = 'Admin'
        if lastName == '':
            lastName = 'Member'

        isSuperadmin = False
        isActive = False
        if User.objects.filter(is_superadmin=True).count()==0:
            isSuperadmin = True
            isActive = True
        try:
            admin = User.objects.create_superuser(email=email, phone=phone, password=password, is_superadmin=isSuperadmin, is_active=isActive, first_name=firstName, last_name=lastName)
            permissions = Permission.objects.all()
            admin.user_permissions.set(permissions)
            messages.success(request, 'Successfully created admin.', extra_tags='success-create-admin')
            return redirect(request.META['HTTP_REFERER'])
        except Exception as e:
            messages.error(request, 'Something went wrong!', extra_tags='error-create-admin')
            return redirect(request.META['HTTP_REFERER'])
    if type=='internal':
        notifications = Notification.objects.filter(is_opened=False, notif_for_id=request.user.id).order_by('-id')
        page_ = 'Create Admin'
        sub_menu = 'Admins'
        data = {
            'notifications':notifications,
            'page_':page_,
            'sub_menu':sub_menu
        }
        return render(request, 'front-end/admin/create-admin-internal.html', data)
    if User.objects.filter(is_superadmin=True).count()==0:
        return render(request, 'front-end/admin/create-superadmin.html')
    return HttpResponse("Have a good day.")
    return render(request, 'front-end/admin/create-admin.html')


def editAdmin(request, adminId=0):
    if request.method == 'POST':
        adminId = request.POST.get('admin-id')
        firstName = request.POST.get('first-name').strip()
        lastName = request.POST.get('last-name').strip()
        email = request.POST.get('email').strip()
        phone = request.POST.get('phone').strip()
        password = request.POST.get('password').strip()
        retypePassword = request.POST.get('retype-password').strip()
    admin = User.objects.get(id=adminId)
    if request.method == 'GET':
        notifications = Notification.objects.filter(is_opened=False, notif_for_id=request.user.id).order_by('-id')
        page_ = 'Edit Admin'
        sub_menu = 'Admins'
        data = {
            'notifications':notifications,
            'admin':admin,
            'page_':page_,
            'sub_menu':sub_menu
        }
        return render(request, 'front-end/admin/edit-admin.html', data)
    if len(firstName)>1:
        admin.first_name = firstName
    else:
        admin.first_name = 'Admin'
    if len(lastName)>1:
        admin.last_name = lastName
    else:
        admin.last_name = 'Member'
    if len(email)>1:
        admin.email = email
    if len(phone)>1:
        admin.phone = phone
    if len(password)>1:
        if password != retypePassword:
            messages.error(request, "Passwords don't match", extra_tags='error-edit-admin')
            return redirect(request.META['HTTP_REFERER'])
        try:
            admin.set_password(password)
        except:
            messages.error(request, 'Could not save password!', extra_tags='error-edit-admin')
            return redirect(request.META['HTTP_REFERER'])
    try:
        admin.save()
        messages.success(request, 'Successfully updated.', extra_tags='success-edit-admin')
    except:
        messages.error(request, 'Something went wrong!', extra_tags='error-edit-admin')
    return redirect(request.META['HTTP_REFERER'])


def adminList(request):
    notifications = Notification.objects.filter(is_opened=False, notif_for_id=request.user.id).order_by('-id')
    admins = User.objects.filter(is_admin=True).all()
    totalPermissions = Permission.objects.count()
    page_ = 'Admin List'
    sub_menu = 'Admins'
    data = {
        'notifications':notifications,
        'admins':admins,
        'total_permissions':totalPermissions,
        'page_':page_,
        'sub_menu':sub_menu
    }
    return render(request, 'front-end/admin/admin-list.html', data)


def loginUser(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)
        if user:
            try:
                login(request, user)
                return redirect('home')
            except:
                return HttpResponse('Something went wrong!')
        else:
            return HttpResponse('Invalid email/password')
    frontPage = FrontPage.objects.all().first()
    data = {
        'front_page':frontPage
    }
    return render(request, 'front-end/admin/login-admin.html', data)
        

@login_required(login_url='login-user')
def home(request):
    # return render(request, 'base-front-end/admin/home-admin.html')
    notifications = Notification.objects.filter(is_opened=False, notif_for_id=request.user.id).order_by('-id')
    if request.user.is_admin == True:
        totalFaultsReported = FaultReport.objects.count()
        avgCompletionTime = FaultReport.objects.aggregate(Avg('completion_time'))
        avgCompletionTime = 0
        daysTakenAvg = 0
        hoursTakenAvg = 0
        minutesTakenAvg = 0
        secondsTakenAvg = 0
        if avgCompletionTime > 0:
            avgCompletionTime = int(avgCompletionTime['completion_time__avg'])
            daysTakenAvg = avgCompletionTime//86400
            remSeconds = avgCompletionTime%86400
            hoursTakenAvg = remSeconds//3600
            remSeconds = remSeconds%3600
            minutesTakenAvg = remSeconds//60
            secondsTakenAvg = remSeconds%60

        urgentComp = FaultReport.objects.filter(status='C', priority_level='U').count()
        urgentCompOnTime = FaultReport.objects.filter(status='C', priority_level='U', is_late=False).count()
        if urgentComp > 0:
            urgeComOnTimePerc = round((urgentCompOnTime/urgentComp)*100, 2)
        else:
            urgeComOnTimePerc = 0
        totalComp = FaultReport.objects.filter(status='C').count()
        totalCompOnTime = FaultReport.objects.filter(status='C', is_late=False).count()
        if totalComp > 0:
            totalCompOnTimePerc = round((totalCompOnTime/totalComp)*100, 2)
        else:
            totalCompOnTimePerc = 0
        data = {
            'notifications':notifications,
            'total_faults_reported':totalFaultsReported,
            'days_taken_avg' : daysTakenAvg,
            'hours_taken_avg' : hoursTakenAvg,
            'minutes_taken_avg' : minutesTakenAvg,
            'seconds_taken_avg' : secondsTakenAvg,
            'urge_com_on_time_perc' : urgeComOnTimePerc,
            'total_comp_on_time_perc' : totalCompOnTimePerc
        }
    elif request.user.is_technician == True:
        totalTasksAssigned = FaultReport.objects.filter(user_technician=request.user).count()
        totalTasksCompleted = FaultReport.objects.filter(completed_at__isnull=False, user_technician=request.user).count()
        completionPercentage = 0
        if totalTasksAssigned > 0:
            completionPercentage = round((totalTasksCompleted/totalTasksAssigned)*100, 2)
        data = {
            'notifications':notifications,
            'total_tasks_assigned':totalTasksAssigned,
            'total_tasks_completed':totalTasksCompleted,
            'completion_percentage':completionPercentage
        }
    elif request.user.is_enduser == True:
        totalFaultReports = FaultReport.objects.filter(contact_email=request.user.email).count()
        totalCompleted = FaultReport.objects.filter(completed_at__isnull=False, contact_email=request.user.email).count()
        compOnTime = FaultReport.objects.filter(completed_at__isnull=False, contact_email=request.user.email, is_late=False).count()
        totalCompPercentage = 0
        compOnTimePerc = 0
        if totalCompleted > 0:
            totalCompPercentage = round((totalCompleted/totalFaultReports)*100, 2)
            compOnTimePerc = round((compOnTime/totalCompleted)*100, 2)
        data={
            'notifications':notifications,
            'total_fault_reports':totalFaultReports,
            'total_completed':totalCompleted,
            'total_comp_percentage':totalCompPercentage,
            'comp_on_time':compOnTime,
            'comp_on_time_percentage':compOnTimePerc
        }

    return render(request, 'front-end/admin/home.html', data)


def logoutAdmin(request):
    logout(request)
    return redirect('login-user')


def permissionList(request, adminId):
    admin = User.objects.get(id=adminId)
    allPermissions = Permission.objects.all()
    data = {
        'admin':admin,
        'permissions':allPermissions
    }
    return render(request, 'front-end/admin/permission-list.html', data)


def updatePermissions(request):
    adminId = request.POST.get('admin-id')
    admin = User.objects.get(id=adminId)

    permissionList = request.POST.getlist('permissions')
    permissions = Permission.objects.filter(id__in=permissionList)

    admin.user_permissions.set(permissions)

    return redirect(request.META['HTTP_REFERER'])