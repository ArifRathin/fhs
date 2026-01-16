from django.http import HttpResponse
from django.shortcuts import render, redirect
from .models import User
from fault_report.models import FaultReport
from front_page.models import FrontPage
from django.db import transaction
from django.contrib import messages

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