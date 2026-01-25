from django.http import HttpResponse
from django.shortcuts import render, redirect
from .models import User
from fault_report.models import FaultReport
from front_page.models import FrontPage
from django.db import transaction
from django.contrib import messages
import random
from fhs.email_sender import sendEmail
from django.urls import reverse
from django.conf import settings
from django.contrib.auth import authenticate, login

def createEndUser(request):
    if request.method == 'POST':
        email = request.POST.get('email').strip()
        phone = request.POST.get('phone').strip()
        if User.objects.filter(email=email).exists():
            messages.error(request, 'User already exists.', extra_tags='error-create-user')
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
        try:
            with transaction.atomic():
                user = User.objects.create_user(first_name=firstName, last_name=lastName, email=email, phone=phone, password=password)
                user.is_active = True
                user.is_enduser = True
                user.save()
                fault_reports = FaultReport.objects.filter(contact_email=user.email)
                for report in fault_reports:
                    report.user_technician.set([user.id])
                messages.success(request, 'Successfully created account', extra_tags='success-create-user')
                return redirect(request.META['HTTP_REFERER'])
        except Exception as e:
            messages.error(request, 'Something went wrong!', extra_tags='error-create-user')
            return redirect(request.META['HTTP_REFERER'])
    frontPage = FrontPage.objects.all().first()
    data = {
        'front_page':frontPage
    }
    return render(request, 'front-end/enduser/create-enduser.html', data)


def sendChangePasswordLink(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        randomCharArr=['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z','a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z','0','1','2','3','4','5','6','7','8','9']
        randomStr = ''
        for _ in range(0,50):
            randomIndex = random.randint(0, 61)
            randomChar = randomCharArr[randomIndex]
            randomStr += randomChar
        try:
            if User.objects.filter(email=email).exists():
                user = User.objects.get(email=email)
                user.change_password_code = randomStr
                user.save()
                subject = "Change password on FHS"
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
            messages.error(request, "Email could not be sent!", extra_tags="error-send-change-password-link")
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