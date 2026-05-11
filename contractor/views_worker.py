from django.shortcuts import render, redirect
from .models import Worker
from django.contrib import messages
from django.core.paginator import Paginator
from notification.models import Notification
from fhs.image_processor import processImage

# Create your views here.
def createWorker(request):
    if request.method == 'POST':
        name = request.POST.get('name').strip()
        if name == '':
            messages.error(request, 'Name is mandatory!', extra_tags='error-create-worker')
            return redirect(request.META['HTTP_REFERER'])
        email = request.POST.get('email').strip()
        if Worker.objects.filter(email=email).exists():
            messages.error(request, 'A worker with a similar email already exists!', extra_tags='error-create-worker')
            return redirect(request.META['HTTP_REFERER'])
        if email == '':
            messages.error(request, 'Email is mandatory!', extra_tags='error-create-worker')
            return redirect(request.META['HTTP_REFERER'])
        contactNo1 = request.POST.get('contact-number1').strip()
        if Worker.objects.filter(contact_no1=contactNo1).exists():
            messages.error(request, 'A worker with a similar primary contact number already exists!', extra_tags='error-create-worker')
            return redirect(request.META['HTTP_REFERER'])
        if contactNo1 == '':
            messages.error(request, 'Contact number 1 is mandatory!', extra_tags='error-create-worker')
            return redirect(request.META['HTTP_REFERER'])
        elif len(contactNo1) > 20:
            messages.error(request, 'Contact number cannot exceed 20 characters.', extra_tags='error-create-worker')
            return redirect(request.META['HTTP_REFERER'])
        contactNo2 = request.POST.get('contact-number2').strip()
        if len(contactNo2) > 20:
            messages.error(request, 'Contact number cannot exceed 20 characters.', extra_tags='error-create-worker')
            return redirect(request.META['HTTP_REFERER'])
        postCode = request.POST.get('post-code').strip()
        if len(postCode) > 12:
            messages.error(request, 'Post code cannot exceed 20 characters.', extra_tags='error-create-worker')
            return redirect(request.META['HTTP_REFERER'])
        ethnicity = request.POST.get('ethnicity').strip()
        if len(ethnicity) > 30:
            messages.error(request, 'Ethnicity cannot exceed 30 characters.', extra_tags='error-create-worker')
            return redirect(request.META['HTTP_REFERER'])
        reliabilityMax = request.POST.get('reliability-max').strip()
        if reliabilityMax != '':
            rmNum = int(float(reliabilityMax))
            if rmNum < 0 or rmNum > 10:
                messages.error(request, 'Max reliability must be between 0 and 10', extra_tags='error-create-worker')
                return redirect(request.META['HTTP_REFERER'])
        else:
            reliabilityMax = None
        travelRadius = request.POST.get('travel-radius').strip()
        if travelRadius != '':
            trNum = int(float(travelRadius))
            if trNum < 0 or trNum > 16000:
                messages.error(request, 'Travel radius must be between 0 and 16000', extra_tags='error-create-worker')
                return redirect(request.META['HTTP_REFERER'])
        else:
            travelRadius = None
        rates = request.POST.get('rates').strip()
        if rates != '':
            rateNum = int(float(rates))
            if rateNum < 0:
                messages.error(request, 'Rates must be a positive amount.', extra_tags='error-create-worker')
                return redirect(request.META['HTTP_REFERER'])
        else:
            rates = None
        tradeName = request.POST.get('trade-name').strip()
        address = request.POST.get('address').strip()
        region = request.POST.get('region').strip()
        vehicle = request.POST.get('has-vehicle').strip()
        if vehicle == '1':
            vehicle = True
        else:
            vehicle = False
        outOfHour = request.POST.get('if-ooh').strip()
        if outOfHour == '1':
            outOfHour = True
        else:
            outOfHour = False
        note = request.POST.get('note').strip()
        specialities = request.POST.get('specialities').strip()
        insurance = request.POST.get('has-insurance').strip()
        if insurance == '1':
            insurance = True
        else:
            insurance = False
        expiryDate = request.POST.get('expiry-date').strip()
        if expiryDate == '':
            expiryDate = None
        photo = request.FILES.get('photo')
        try:
            worker = Worker.objects.create(name=name, trade_name=tradeName, address=address, post_code=postCode,
                                  region=region, email=email, contact_no1=contactNo1, contact_no2=contactNo2,
                                  ethnicity=ethnicity, reliability_max=reliabilityMax, travel_radius=travelRadius,
                                  vehicle=vehicle, out_of_hour=outOfHour, note=note, rates=rates, specialities=specialities,
                                  insurance=insurance, expiry_date=expiryDate)
            photo = processImage(photo)
            worker.photo = photo
            worker.save()
            messages.success(request, 'Successfully created worker.', extra_tags='success-create-worker')
            return redirect(request.META['HTTP_REFERER'])
        except Exception as e:
            messages.error(request, str(e), extra_tags='error-create-worker')
            return redirect(request.META['HTTP_REFERER'])
    else:
        notifications = Notification.objects.filter(is_opened=False, notif_for_id=request.user.id).order_by('-id')
        data = {
            'notifications':notifications,
            'page_':'Create Worker',
            'sub_menu':'Contractor'
        }
        return render(request, 'worker/create-worker.html', data)
    

def workerList(request):
    workers = Worker.objects.only('name', 'trade_name', 'email', 'contact_no1', 'address', 'out_of_hour')
    pages = Paginator(workers, 10)
    pageNum = request.GET.get('page')
    workers = pages.get_page(pageNum)
    notifications = Notification.objects.filter(is_opened=False, notif_for_id=request.user.id).order_by('-id')
    data = {
        'notifications':notifications,
        'page_':'Worker List',
        'sub_menu':'Contractor',
        'workers':workers
    }
    return render(request, 'worker/worker-list.html', data)


def editWorker(request, workerId=0):
    if request.method == 'POST':
        workerId = request.POST.get('worker-id').strip()
        if not Worker.objects.filter(id=workerId).exists():
            messages.error(request, "Worker doesn't exist!", extra_tags='error-edit-worker')
            return redirect(request.META['HTTP_REFERER'])
        name = request.POST.get('name').strip()
        email = request.POST.get('email').strip()
        if email != '':
            if Worker.objects.filter(email=email).exclude(id=workerId).exists():
                messages.error(request, 'The email you entered belongs to another worker!', extra_tags='error-edit-worker')
                return redirect(request.META['HTTP_REFERER'])
        contactNo1 = request.POST.get('contact-number1').strip()
        if contactNo1 != '':
            if Worker.objects.filter(contact_no1=contactNo1).exclude(id=workerId).exists():
                messages.error(request, 'The primary contact number you entered belongs to another worker!', extra_tags='error-edit-worker')
                return redirect(request.META['HTTP_REFERER'])
        if len(contactNo1) > 20:
            messages.error(request, 'Contact number cannot exceed 20 characters.', extra_tags='error-edit-worker')
            return redirect(request.META['HTTP_REFERER'])
        contactNo2 = request.POST.get('contact-number2').strip()
        if len(contactNo2) > 20:
            messages.error(request, 'Contact number cannot exceed 20 characters.', extra_tags='error-edit-worker')
            return redirect(request.META['HTTP_REFERER'])
        postCode = request.POST.get('post-code').strip()
        if len(postCode) > 12:
            messages.error(request, 'Post code cannot exceed 20 characters.', extra_tags='error-edit-worker')
            return redirect(request.META['HTTP_REFERER'])
        ethnicity = request.POST.get('ethnicity').strip()
        if len(ethnicity) > 30:
            messages.error(request, 'Ethnicity cannot exceed 30 characters.', extra_tags='error-edit-worker')
            return redirect(request.META['HTTP_REFERER'])
        reliabilityMax = request.POST.get('reliability-max').strip()
        if reliabilityMax != '':
            rmNum = int(float(reliabilityMax))
            if rmNum < 0 or rmNum > 10:
                messages.error(request, 'Max reliability must be between 0 and 10', extra_tags='error-edit-worker')
                return redirect(request.META['HTTP_REFERER'])
        else:
            reliabilityMax = None
        travelRadius = request.POST.get('travel-radius').strip()
        if travelRadius != '':
            trNum = int(float(travelRadius))
            if trNum < 0 or trNum > 16000:
                messages.error(request, 'Travel radius must be between 0 and 16000', extra_tags='error-edit-worker')
                return redirect(request.META['HTTP_REFERER'])
        else:
            travelRadius = None
        rates = request.POST.get('rates').strip()
        if rates != '':
            rateNum = int(float(rates))
            if rateNum < 0:
                messages.error(request, 'Rates must be a positive amount.', extra_tags='error-edit-worker')
                return redirect(request.META['HTTP_REFERER'])
        else:
            rates = None
        tradeName = request.POST.get('trade-name').strip()
        address = request.POST.get('address').strip()
        region = request.POST.get('region').strip()
        vehicle = request.POST.get('has-vehicle').strip()
        if vehicle == '0':
            vehicle = False
        else:
            vehicle = True
        outOfHour = request.POST.get('if-ooh').strip()
        if outOfHour == '0':
            outOfHour = False
        else:
            outOfHour = True
        note = request.POST.get('note').strip()
        specialities = request.POST.get('specialities').strip()
        insurance = request.POST.get('has-insurance').strip()
        if insurance == '0':
            insurance = False
        else:
            insurance = True
        expiryDate = request.POST.get('expiry-date').strip()
        if expiryDate == '':
            expiryDate = None
        photo = request.FILES.get('photo')
        if photo:
            photo = processImage(photo)
    worker = Worker.objects.filter(id=workerId).first()
    if worker:
        if request.method == 'GET':
            notifications = Notification.objects.filter(is_opened=False, notif_for_id=request.user.id).order_by('-id')
            data = {
                'notifications':notifications,
                'page_':'Edit Worker',
                'sub_menu':'Contractor',
                'worker':worker
            }
            return render(request, 'worker/edit-worker.html', data)
        else:
            try:
                if name != '':
                    worker.name = name
                if email != '':
                    worker.email = email
                if contactNo1 != '':
                    worker.contact_no1 = contactNo1
                worker.trade_name = tradeName
                worker.address = address
                worker.post_code = postCode
                worker.region = region
                worker.contact_no2 = contactNo2
                worker.ethnicity = ethnicity
                worker.reliability_max = reliabilityMax
                worker.travel_radius = travelRadius
                worker.vehicle = vehicle
                worker.out_of_hour = outOfHour
                worker.note = note
                worker.rates = rates
                worker.specialities = specialities
                worker.insurance = insurance
                worker.expiry_date = expiryDate
                if photo != None:
                    worker.photo = photo
                worker.save()

                messages.success(request, 'Successfully updated worker', extra_tags='success-edit-worker')
                return redirect(request.META['HTTP_REFERER'])
            except Exception as e:
                messages.success(request, 'Something went wrong!', extra_tags='error-edit-worker')
                return redirect(request.META['HTTP_REFERER'])
    else:
        messages.error(request, "Worker doesn't exist!", extra_tags='error-edit-worker')
        return redirect(request.META['HTTP_REFERER'])


def deleteWorker(request, workerId):
    try:
        worker = Worker.objects.filter(id=workerId).first()
        if worker:
            worker.photo.delete(save=False)
            worker.delete()
            messages.success(request, 'Successfully deleted the worker', extra_tags='success-delete-worker')
            return redirect(request.META['HTTP_REFERER'])
        else:
            messages.success(request, "Couldn't delete the worker!", extra_tags='error-delete-worker')
            return redirect(request.META['HTTP_REFERER'])
    except Exception as e:
        messages.success(request, "Couldn't delete the worker!", extra_tags='error-delete-worker')
        return redirect(request.META['HTTP_REFERER'])