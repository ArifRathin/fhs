from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from notification.models import Notification
from .models import User
from fault_report.models import FaultReport, FaultReportImage, PriorityLevel, ReportStatus
from front_page.models import FrontPage
from django.db import transaction
from django.contrib import messages
import random
from fhs.email_sender import sendEmail
from django.urls import reverse
from django.conf import settings
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Sum, Count, F, Value
from quotation.models import Quotation
from address.models import Organization, Location


def createEndUser(request, email=None):
    if request.method == 'POST':
        email = request.POST.get('email').strip()
        phone = request.POST.get('phone').strip()
        if User.objects.filter(email=email).exists():
            messages.error(request, 'User already exists!', extra_tags='error-create-user')
            return redirect(request.META['HTTP_REFERER'])
        elif email == '':
            messages.error(request, 'Email is required!', extra_tags='error-create-user')
            return redirect(request.META['HTTP_REFERER'])
        if User.objects.filter(phone=phone).exists():
            messages.error(request, 'Phone number already exists!', extra_tags='error-create-user')
            return redirect(request.META['HTTP_REFERER'])
        elif len(phone) > 16:
            messages.error(request, 'Phone number is too long!', extra_tags='error-create-user')
            return redirect(request.META['HTTP_REFERER'])
        elif phone == '':
            messages.error(request, 'Phone number is required!', extra_tags='error-create-user')
            return redirect(request.META['HTTP_REFERER'])
        password = request.POST.get('password')
        if len(password) < 6:
            messages.error(request, 'Password has to be at least 6 characters.', extra_tags='error-create-user')
            return redirect(request.META['HTTP_REFERER'])
        retypePassword = request.POST.get('retype-password')
        if password != retypePassword:
            messages.error(request, "Passwords don't match.", extra_tags='error-create-user')
            return redirect(request.META['HTTP_REFERER'])

        firstName = request.POST.get('first-name').strip()
        lastName = request.POST.get('last-name').strip()
        if firstName == '' or lastName == '':
            messages.error(request, 'Both first name and last name are required.', extra_tags='error-create-user')
            return redirect(request.META['HTTP_REFERER'])
        firstName = firstName.title()
        lastName = lastName.title()
        organizationName = request.POST.get('organization-name').strip()
        organizationName = organizationName.title()
        address = request.POST.get('address').strip()
        address = address.capitalize()
        if address == '':
            messages.error(request, 'Address is mandatory!', extra_tags='error-create-user')
            return redirect(request.META['HTTP_REFERER'])
        postalCode = request.POST.get('postal-code').strip()
        if postalCode == '':
            messages.error(request, 'Postal code is mandatory!', extra_tags='error-create-user')
            return redirect(request.META['HTTP_REFERER'])
        elif len(postalCode) > 12:
            messages.error(request, 'Postal code is too long!', extra_tags='error-create-user')
            return redirect(request.META['HTTP_REFERER'])
        try:
            with transaction.atomic():
                user = User.objects.create_user(first_name=firstName, last_name=lastName, email=email, phone=phone, password=password)
                user.is_enduser = True
                if request.user.is_authenticated and request.user.is_admin:
                    user.is_active = True
                user.account_activation_code = generateRandomStr()
                if user.id < 10:
                    toSub = 1
                elif user.id < 100:
                    toSub = 2
                elif user.id < 1000:
                    toSub = 3
                elif user.id < 100000:
                    toSub = 4
                elif user.id < 1000000:
                    toSub = 5
                accountNumber = 'FH'
                for _ in range(0,(5-toSub)):
                    accountNumber += '0'
                accountNumber += str(user.id)
                user.account_number = accountNumber
                if organizationName != '':
                    user.organization_name = organizationName
                user.address = address
                user.post_code = postalCode
                user.save()
                fault_reports = FaultReport.objects.filter(contact_email=user.email)
                for report in fault_reports:
                    report.user_technician.set([user.id])
                if request.user.is_authenticated and request.user.is_admin:
                    messages.success(request, 'Successfully created customer.', extra_tags='success-create-user')
                    return redirect('customer-list')
                else:
                    messages.success(request, 'Please check your email to activate your account.', extra_tags='success-create-user')
                    return redirect(request.META['HTTP_REFERER'])
        except Exception as e:
            messages.error(request, str(e), extra_tags='error-create-user')
            return redirect(request.META['HTTP_REFERER'])
    frontPage = FrontPage.objects.all().first()
    data = {
        'front_page':frontPage,
        'sub_menu':'Customers',
        'page_':'Create Customer',
        'email':email
    }
    if request.user.is_authenticated and request.user.is_admin:
        return render(request, 'front-end/admin/create-enduser-internal.html', data)
    return render(request, 'front-end/enduser/create-enduser.html', data)


@permission_required('account.change_user', login_url='login-user', raise_exception=True)
def editEndUser(request, email=None):
    if request.method == 'POST':
        accountNumber = request.POST.get('account-number').strip()
        if accountNumber == '':
            messages.error(request, 'Invalid input!', extra_tags='error-edit-user')
            return redirect(request.META['HTTP_REFERER'])
        elif not User.objects.filter(account_number=accountNumber).exists():
            messages.error(request, 'Customer not found!', extra_tags='error-edit-user')
            return redirect(request.META['HTTP_REFERER'])
        customer = User.objects.filter(account_number=accountNumber).first()
        email = request.POST.get('email').strip()
        if email == '':
            messages.error(request, 'Email is mandatory!', extra_tags='error-edit-user')
            return redirect(request.META['HTTP_REFERER'])
        elif User.objects.filter(email=email).exclude(account_number=accountNumber).exists():
            messages.error(request, 'This email belongs to another account!', extra_tags='error-edit-user')
            return redirect(request.META['HTTP_REFERER'])
        phone = request.POST.get('phone').strip()
        if phone == '':
            messages.error(request, 'Phone number is mandatory!', extra_tags='error-edit-user')
            return redirect(request.META['HTTP_REFERER'])
        elif User.objects.filter(phone=phone).exclude(account_number=accountNumber).exists():
            messages.error(request, 'This phone number belongs to another account!', extra_tags='error-edit-user')
            return redirect(request.META['HTTP_REFERER'])
        firstName = request.POST.get('first-name').strip()
        if firstName == '':
            messages.error(request, 'First name is mandatory!', extra_tags='error-edit-user')
            return redirect(request.META['HTTP_REFERER'])
        lastName = request.POST.get('last-name').strip()
        if lastName == '':
            messages.error(request, 'Last name is mandatory!', extra_tags='error-edit-user')
            return redirect(request.META['HTTP_REFERER'])
        organizationName = request.POST.get('organization-name').strip()
        address = request.POST.get('address').strip()
        if address == '':
            messages.error(request, 'Address is mandatory!', extra_tags='error-edit-user')
            return redirect(request.META['HTTP_REFERER'])
        postalCode = request.POST.get('postal-code').strip()
        if postalCode == '':
            messages.error(request, 'Postal code is mandatory!', extra_tags='error-edit-user')
            return redirect(request.META['HTTP_REFERER'])
        isActive = request.POST.get('is-active').strip()
        if isActive == '0':
            isActive = False
        elif isActive == '1':
            isActive = True
        else:
            messages.error(request, 'Invalid input!', extra_tags='error-edit-user')
            return redirect(request.META['HTTP_REFERER'])
        password = request.POST.get('password').strip()
        if password != '':
            retypePassword = request.POST.get('retype-password').strip()
            if password != retypePassword:
                messages.error(request, "Passwords don't match!", extra_tags='error-edit-user')
                return redirect(request.META['HTTP_REFERER'])
            if len(password) < 6:
                messages.error(request, 'Password has to be at least 6 characters!', extra_tags='error-edit-user')
                return redirect(request.META['HTTP_REFERER'])

    if request.method == 'GET':
        customer = User.objects.filter(email=email).first()
        if customer == None:
            return redirect('create-enduser', email=email)
        notifications = Notification.objects.filter(is_opened=False, notif_for_id=request.user.id).order_by('-id')
        # organizations = Organization.objects.filter(is_active=True)
        # locations = Location.objects.filter(is_active=True)
        data = {
            'notifications':notifications,
            # 'organizations':organizations,
            # 'locations':locations,
            'email':email,
            'customer':customer,
            'sub_menu':'Customers',
            'page_':'Edit Customer'
        }
    
        return render(request, 'front-end/admin/edit-enduser-internal.html', data)
    try:
        with transaction.atomic():
            customer.email = email
            customer.phone = phone
            customer.first_name = firstName
            customer.last_name = lastName
            if organizationName != '':
                customer.organization_name = organizationName
            customer.address = address
            customer.post_code = postalCode
            customer.is_active = isActive
            if password != '':
                customer.set_password(password)
            customer.save()
            messages.success(request, 'Successfully updated.', extra_tags='success-edit-user')
            return redirect('edit-enduser', email=email)
    except Exception as e:
        messages.error(request, str(e), extra_tags='error-edit-user')
        return redirect('edit-enduser', email=email)


@permission_required('account.delete_user', login_url='login-user', raise_exception=True)
def deleteEndUser(request, email):
    try:
        with transaction.atomic():
            if User.objects.filter(email=email).exists():
                User.objects.get(email=email).delete()
            faultReports = FaultReport.objects.filter(contact_email=email)
            for report in faultReports:
                faultReportImages = FaultReportImage.objects.filter(fault_report_id=report.id)
                for image in faultReportImages:
                    image.image.delete(save=False)
                    image.delete()
                report.delete()
            messages.success(request, 'Successfully deleted the customer.', extra_tags='success-delete-user')
            return redirect(request.META['HTTP_REFERER'])
    except:
        messages.error(request, 'Something went wrong!', extra_tags='error-delete-user')
        return redirect(request.META['HTTP_REFERER'])


def activateAccount(request, code):
    try:
        if User.objects.filter(account_activation_code=code).exists():
            user = User.objects.get(account_activation_code=code)
            user.is_active = True
            user.account_activation_code = None
            user.save()
            messages.success(request, 'Account activated!', extra_tags='success-activate-account')
            return redirect('home')
        else:
            messages.error(request, "This account doesn't exist", extra_tags='error-activate-account')
            return redirect('create-enduser')
    except:
        messages.error(request, "Something went wrong!", extra_tags='error-activate-account')
        return redirect('create-enduser')

@permission_required('account.view_user', login_url='login-user', raise_exception=True)
def customerList(request):
    notifications = Notification.objects.filter(is_opened=False, notif_for_id=request.user.id).order_by('-id')
    customersWithReports= FaultReport.objects.values(email=F('contact_email')).annotate(count=Count('id')).values('email', 'count')
    customersWithoutReports = User.objects.exclude(email__in=FaultReport.objects.values('contact_email')).filter(is_enduser=True).values('email').annotate(count=Value(0)).values('email','count')
    customers = customersWithReports.union(customersWithoutReports).order_by('-count')
    data = {
        'notifications':notifications,
        'sub_menu':'Customers',
        'page_':'Customer List',
        'customers':customers
    }
    return render(request, 'front-end/enduser/enduser-list.html', data)

@permission_required('account.view_user', login_url='login-user', raise_exception=True)
def customerHistory(request, customerEmail):
    notifications = Notification.objects.filter(is_opened=False, notif_for_id=request.user.id).order_by('-id')
    history = FaultReport.objects.filter(contact_email=customerEmail).order_by('-created_at')
    totalReports = FaultReport.objects.filter(contact_email=customerEmail).count()
    totalbill = Quotation.objects.filter(fault_report__contact_email=customerEmail, approval_status='QA').aggregate(total_bill=Sum('total_bill'))
    isRegistered = User.objects.filter(email=customerEmail).exists()
    user = None
    if isRegistered:
        user = User.objects.get(email=customerEmail)
    data={
        'notifications':notifications,
        'sub_menu':'Customers',
        'page_':'Customer History',
        'customer':user,
        'is_registered':isRegistered,
        'customer_email':customerEmail,
        'customer_history':history,
        'total_reports':totalReports,
        'total_bill':totalbill['total_bill'],
        'priority_levels':PriorityLevel.choices,
        'statuses':ReportStatus.choices
    }
    return render(request, 'front-end/enduser/enduser-history.html', data)


def sendChangePasswordLink(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        randomStr = generateRandomStr()
        try:
            if User.objects.filter(email=email).exists():
                user = User.objects.get(email=email)
                user.change_password_code = randomStr
                user.save()
                subject = "Change password!!"
                to = []
                to.append(email)
                body = 'front-end/emails/send-change-password-link-email.html'
                baseLink = settings.BASIC_URL
                link = reverse('change-password', args=[randomStr])
                fullLink = f"{baseLink}{link}"
                context = {
                    'receiver_name':user.first_name,
                    'full_link':fullLink
                }
                sendEmail.delay(subject=subject, to=to, body=body, context=context)
                messages.success(request, "We have sent an email to your email address.", extra_tags="success-send-change-password-link")
                return redirect(request.META['HTTP_REFERER'])
            else:
                messages.error(request, "Email could not be sent!!", extra_tags="error-send-change-password-link")
                return redirect(request.META['HTTP_REFERER'])
        except Exception as e:
            messages.error(request, str(e), extra_tags="error-send-change-password-link")
            return redirect(request.META['HTTP_REFERER'])

    frontPage = FrontPage.objects.all().first()
    data={
        'front_page':frontPage,
        'page_':'Change password'
    }
    return render(request, 'front-end/send-change-password-link.html', data)


def changePassword(request, code=0):
    if request.method == 'POST':
        newPassword = request.POST.get('new-password')
        retypePassword = request.POST.get('retype-password')
        if newPassword != retypePassword:
            messages.error(request, "Passwords don't match!", extra_tags="error-change-password")
            return redirect(request.META['HTTP_REFERER'])
        code = request.POST.get('change-password-code').strip()
        try:
            if User.objects.filter(change_password_code=code).exists():
                user = User.objects.get(change_password_code=code)
                user.set_password(newPassword)
                user.change_password_code = None
                user.save()
                loggedUser = authenticate(request, email=user.email, password=newPassword)
                if loggedUser:
                    login(request, loggedUser)
                    return redirect('home')
                else:
                    messages.error(request, "Password changed but failed to log in!", extra_tags="error-change-password")
                    return redirect(request.META['HTTP_REFERER'])
            else:
                messages.error(request, "The link is invalid or expired!", extra_tags="error-change-password")
                return redirect(request.META['HTTP_REFERER'])
        except Exception as e:
            messages.error(request, 'Something went wrong!', extra_tags="error-change-password")
            return redirect(request.META['HTTP_REFERER'])
    frontPage = FrontPage.objects.all().first()
    data = {
        'page_':"Change Password",
        'front_page':frontPage,
        'code':code
    }
    return render(request, 'front-end/change-password.html', data)


def generateRandomStr():
    randomCharArr=['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z','a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z','0','1','2','3','4','5','6','7','8','9']
    randomStr = ''
    for _ in range(0,50):
        randomIndex = random.randint(0, 61)
        randomChar = randomCharArr[randomIndex]
        randomStr += randomChar

    return randomStr


def getLocFromOrg(request):
    organizationId = request.GET.get('organizationId')
    organiation = Organization.objects.filter(id=organizationId).first()
    locations = []
    if organiation:
        locations = organiation.location.filter(is_active=True).values('id', 'name')
    return JsonResponse(list(locations), safe=False)