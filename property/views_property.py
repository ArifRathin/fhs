from django.shortcuts import render, redirect
from notification.models import Notification
from property.models import Property, VisitingDates
from django.db import transaction
from django.contrib import messages

# Create your views here.
def createProperty(request):
    if request.method == 'POST':
        name = request.POST.get('name').strip()
        if name == '':
            messages.error(request, 'Name is mandatory!', extra_tags='error-create-property')
            return redirect(request.META['HTTP_REFERER'])
        address = request.POST.get('address').strip()
        if address == '':
            messages.error(request, 'Address is mandatory!', extra_tags='error-create-property')
            return redirect(request.META['HTTP_REFERER'])
        notes = request.POST.get('notes').strip()

        visitingDates = request.POST.getlist('visiting-dates')
        if len(visitingDates) == 0:
            messages.error(request, 'Visiting date is mandatory!', extra_tags='error-create-property')
            return redirect(request.META['HTTP_REFERER'])

        try:
            with transaction.atomic():
                property = Property.objects.create(name=name, address=address, notes=notes)
                for date in visitingDates:
                    VisitingDates.objects.create(property=property, visiting_date=date)
                messages.success(request, 'Successfully created property.', extra_tags='success-create-property')
                return redirect(request.META['HTTP_REFERER'])
        except Exception as e: 
            messages.error(request, str(e), extra_tags='error-create-property')
            return redirect(request.META['HTTP_REFERER'])
    notifications = Notification.objects.filter(is_opened=False, notif_for_id=request.user.id).order_by('-id')
    data = {
        'notifications':notifications,
        'sub_menu':'Properties',
        'page_':'Create Property'
    }
    return render(request, 'property/create-property.html', data)


def propertyList(request):
    properties = Property.objects.all()
    notifications = Notification.objects.filter(is_opened=False, notif_for_id=request.user.id).order_by('-id')
    data = {
        'notifications':notifications,
        'sub_menu':'Properties',
        'page_':'Property List',
        'properties':properties
    }
    return render(request, 'property/property-list.html', data)


def editProperty(request, propertyId=0):
    if request.method == 'POST':
        propertyId = request.POST.get('property-id')
        name = request.POST.get('name').strip()
        if name == '':
            messages.error(request, 'Name is mandatory!', extra_tags='error-edit-property')
            return redirect(request.META['HTTP_REFERER'])
        address = request.POST.get('address').strip()
        if address == '':
            messages.error(request, 'Address is mandatory!', extra_tags='error-edit-property')
            return redirect(request.META['HTTP_REFERER'])
        notes = request.POST.get('notes').strip()

        visitingDates = request.POST.getlist('visiting-dates')

    property = Property.objects.filter(id=propertyId).first()
    if property != None:
        if request.method == 'GET':
            notifications = Notification.objects.filter(is_opened=False, notif_for_id=request.user.id).order_by('-id')
            data = {
                'property':property,
                'notifications':notifications,
                'sub_menu':'Properties',
                'page_':'Edit Property'
            }
            return render(request, 'property/edit-property.html', data)
        elif request.method == 'POST':
            try:
                with transaction.atomic():
                    property.name = name
                    property.address = address
                    property.notes = notes
                    property.save()
                    property.visits.all().delete()
                    dateArr = []
                    for date in visitingDates:
                        if date != '':
                            dateArr.append(VisitingDates(property=property, visiting_date=date))
                    if dateArr:
                        VisitingDates.objects.bulk_create(dateArr)
                    messages.error(request, 'Successfully updated property.', extra_tags='success-edit-property')
                    return redirect(request.META['HTTP_REFERER'])
            except Exception as e:
                messages.error(request, "Something went wrong!", extra_tags='error-edit-property')
                return redirect(request.META['HTTP_REFERER'])
    else:
        messages.error(request, 'Property record not found!', extra_tags='error-edit-property')
        return redirect(request.META['HTTP_REFERER'])
    

def deleteProperty(request, propertyId):
    try:
        with transaction.atomic():
            property = Property.objects.filter(id=propertyId).first()
            if property == None:
                messages.error(request, 'Property not found!', extra_tags='success-create-property')
                return redirect(request.META['HTTP_REFERER'])
            property.delete()
            messages.error(request, 'Successfully deleted the property.', extra_tags='success-delete-property')
            return redirect(request.META['HTTP_REFERER'])
    except Exception as e:
        messages.error(request, 'Something went wrong!', extra_tags='success-delete-property')
        return redirect(request.META['HTTP_REFERER'])