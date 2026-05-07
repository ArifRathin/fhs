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
        tradeName = request.POST.get('trade-name').strip()
        address = request.POST.get('address').strip()
        postCode = request.POST.get('post-code').strip()
        region = request.POST.get('region').strip()
        email = request.POST.get('email').strip()
        contactNo1 = request.POST.get('contact-number1').strip()
        contactNo2 = request.POST.get('contact-number2').strip()
        ethnicity = request.POST.get('ethnicity').strip()
        reliabilityMax = request.POST.get('reliability-max').strip()
        travelRadius = request.POST.get('travel-radius').strip()
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
        rates = request.POST.get('rates').strip()
        specialities = request.POST.get('specialities').strip()
        insurance = request.POST.get('has-insurance').strip()
        if insurance == '0':
            insurance = False
        else:
            insurance = True
        expiryDate = request.POST.get('expiry-date').strip()
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
            messages.error(request, 'Something went wrong!', extra_tags='error-create-worker')
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
        name = request.POST.get('name').strip()
        tradeName = request.POST.get('trade-name').strip()
        address = request.POST.get('address').strip()
        postCode = request.POST.get('post-code').strip()
        region = request.POST.get('region').strip()
        email = request.POST.get('email').strip()
        contactNo1 = request.POST.get('contact-number1').strip()
        contactNo2 = request.POST.get('contact-number2').strip()
        ethnicity = request.POST.get('ethnicity').strip()
        reliabilityMax = request.POST.get('reliability-max').strip()
        travelRadius = request.POST.get('travel-radius').strip()
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
        rates = request.POST.get('rates').strip()
        specialities = request.POST.get('specialities').strip()
        insurance = request.POST.get('has-insurance').strip()
        if insurance == '0':
            insurance = False
        else:
            insurance = True
        expiryDate = request.POST.get('expiry-date').strip()
        photo = request.FILES.get('photo')
        if photo:
            photo = processImage(photo)
        else:
            photo = None
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
                worker.name = name
                worker.trade_name = tradeName
                worker.address = address
                worker.post_code = postCode
                worker.region = region
                worker.email = email
                worker.contact_no1 = contactNo1
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