from django.shortcuts import render, HttpResponse, redirect
from .models import User
from notification.models import Notification
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.contrib import messages

@login_required(login_url='technician-login')
def createTechnician(request):
    if request.method == 'POST':
        firstName = request.POST.get('first-name').strip()
        if firstName == '':
            firstName = 'Technician'
        lastName = request.POST.get('last-name').strip()
        if lastName == '':
            lastName = 'Staff'
        email = request.POST.get('email').strip()
        if email == '':
            messages.error(request, 'Email is required', extra_tags='error-create-technician')
            return redirect(request.META['HTTP_REFERER'])
        phone = request.POST.get('phone').strip()
        if phone == '':
            messages.error(request, 'Phone is required', extra_tags='error-create-technician')
            return redirect(request.META['HTTP_REFERER'])
        password = request.POST.get('password').strip()
        if password == '':
            messages.error(request, 'Password is required', extra_tags='error-create-technician')
            return redirect(request.META['HTTP_REFERER'])
        retypePassword = request.POST.get('retype-password').strip()
        if retypePassword == '':
            messages.error(request, 'Please re-type the password', extra_tags='error-create-technician')
            return redirect(request.META['HTTP_REFERER'])
            
        try:
            with transaction.atomic():
                technician = User.objects.create_user(first_name=firstName, last_name=lastName, email=email, phone=phone, password=password)
                technician.is_staff = True
                technician.is_active = True
                technician.is_technician = True
                technician.save()
                messages.success(request, 'Successfully created technician.', extra_tags='success-create-technician')
                return redirect(request.META['HTTP_REFERER'])
        except Exception as e:
            messages.error(request, 'Something went wrong!', extra_tags='error-create-technician')
            return redirect(request.META['HTTP_REFERER'])
    notifications = Notification.objects.filter(is_opened=False, notif_for_id=request.user.id).order_by('-id')
    page_ = 'Create Technician'
    sub_menu = 'Technicians'
    data = {
        'notifications':notifications,
        'page_':page_,
        'sub_menu':sub_menu
    }
    return render(request, 'front-end/technician/create-technician.html', data)


def technicianList(request):
    notifications = Notification.objects.filter(is_opened=False, notif_for_id=request.user.id).order_by('-id')
    technicians = User.objects.filter(is_technician=True)
    page_ = 'Technician List'
    sub_menu = 'Technicians'
    data = {
        'notifications':notifications,
        'technicians':technicians,
        'page_':page_,
        'sub_menu':sub_menu
    }
    return render(request, 'front-end/technician/technician-list.html', data)


def editTechnician(request, technicianId=0):
    if request.method == 'POST':
        technicianId = request.POST.get('technician-id')
        firstName = request.POST.get('first-name').strip()
        if firstName == '':
            firstName = 'Technical'
        lastName = request.POST.get('last-name').strip()
        if lastName == '':
            lastName = 'Staff'
        email = request.POST.get('email').strip()
        if email == '':
            messages.error(request, 'Email is required', extra_tags='error-edit-technician')
            return redirect(request.META['HTTP_REFERER'])
        phone = request.POST.get('phone').strip()
        if phone == '':
            messages.error(request, 'Phone is required', extra_tags='error-edit-technician')
            return redirect(request.META['HTTP_REFERER'])
        password = request.POST.get('password').strip()
        if password != '':
            retypePassword = request.POST.get('retype-password').strip()
            if password != retypePassword:
                messages.error(request, "Passwords don't match!", extra_tags='error-edit-technician')
                return redirect(request.META['HTTP_REFERER'])
    notifications = Notification.objects.filter(is_opened=False, notif_for_id=request.user.id).order_by('-id')
    technician = User.objects.get(id=technicianId)
    if request.method == 'GET':
        page_ = 'Edit Technician'
        sub_menu = 'Technicians'
        data = {
            'notifications':notifications,
            'technician':technician,
            'page_':page_,
            'sub_menu':sub_menu
        }
        return render(request, 'front-end/technician/edit-technician.html', data)
    technician.first_name = firstName
    technician.last_name = lastName
    technician.email = email
    technician.phone = phone
    try:
        with transaction.atomic():
            technician.save()
            technician.set_password(password)
            messages.success(request, "Successfully updated.", extra_tags='success-edit-technician')
            return redirect(request.META['HTTP_REFERER'])
    except Exception as e:
        messages.error(request, "Something went wrong!", extra_tags='error-edit-technician')
        return redirect(request.META['HTTP_REFERER'])
