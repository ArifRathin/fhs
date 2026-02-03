from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Location, Organization
from django.db import transaction
# Create your views here.
def createLocation(request):
    if request.method == 'POST':
        name = request.POST.get('location-name').strip()
        if name == '' or name == None:
            messages.error(request, 'Location name is mandatory!', extra_tags='error-create-location')
            return redirect(request.META['HTTP_REFERER'])
        address = request.POST.get('address').strip()
        if address == '':
            address = None
        isActive = request.POST.get('is-active').strip()
        if isActive == '1':
            isActive = True
        elif isActive == '0':
            isActive = False
        else:
            messages.error(request, 'Invalid input!', extra_tags='error-create-location')
            return redirect(request.META['HTTP_REFERER'])
        try:
            Location.objects.create(name=name, address=address, is_active=isActive)

            messages.success(request, 'Successfully created location', extra_tags='success-create-location')
            return redirect(request.META['HTTP_REFERER'])
        except Exception as e:
            messages.success(request, 'Something went wrong!', extra_tags='error-create-location')
            return redirect(request.META['HTTP_REFERER'])
    data = {
        'page_':'Create Location',
        'sub_menu':'Address',
        'sub_menu2':'Location'
    }
    return render(request, 'front-end/location/create-location.html', data)


def locationList(request):
    locations = Location.objects.all().order_by('name')
    data = {
        'locations':locations,
        'sub_menu':'Address',
        'sub_menu2':'Location',
        'page_':'Location List'
    }
    return render(request, 'front-end/location/location-list.html', data)


def editLocation(request, locationId=0):
    if request.method == "POST":
        locationId = request.POST.get('location-id').strip()
        if locationId == '':
            messages.error(request, 'Invalid input!', extra_tags='error-create-location')
            return redirect(request.META['HTTP_REFERER']) 
        name = request.POST.get('location-name').strip()
        if name == '':
            messages.error(request, 'Location name is a mandatory field!', extra_tags='success-edit-location')
            return redirect(request.META['HTTP_REFERER'])
        address = request.POST.get('address').strip()
        if address == '':
            address = None
        isActive = request.POST.get("is-active").strip()
        if isActive == '1':
            isActive = True
        elif isActive == '0':
            isActive = False
        else:
            messages.error(request, 'Invalid input!', extra_tags='error-create-location')
            return redirect(request.META['HTTP_REFERER'])      
    location = Location.objects.get(id=locationId)
    if request.method == 'GET':
        data = {
            'location':location,
            'page_':'Edit Location',
            'sub_menu':'Address',
            'sub_menu2':'Location'
        }
        return render(request, 'front-end/location/edit-location.html', data)
    try:
        location.name = name
        location.address = address
        location.is_active = isActive

        location.save()

        messages.success(request, 'Successfully edited location.', extra_tags='success-edit-location')
        return redirect(request.META['HTTP_REFERER'])
    except Exception as e:
        messages.error(request, 'Something went wrong!', extra_tags='error-edit-location')
        return redirect(request.META['HTTP_REFERER'])
    

def createOrganization(request):
    if request.method == 'POST':
        locations = request.POST.getlist('location-id')
        if len(locations) == 0:
            messages.error(request, 'Invalid input!', extra_tags='error-create-organization')
            return redirect(request.META['HTTP_REFERER'])
        name = request.POST.get('organization-name').strip()
        if name == '':
            messages.error(request, 'Invalid input!', extra_tags='error-create-organization')
            return redirect(request.META['HTTP_REFERER'])
        isActive = request.POST.get('is-active').strip()
        if isActive == '0':
            isActive = False
        elif isActive == '1':
            isActive = True
        else:
            messages.error(request, 'Invalid input!', extra_tags='error-create-organization')
            return redirect(request.META['HTTP_REFERER'])
        try:
            with transaction.atomic():
                organization = Organization.objects.create(name=name, is_active=isActive)
                locationIds = [int(id) for id in locations]
                organization.location.set(locationIds)
                messages.success(request, 'Successfully created organization', extra_tags='success-create-organization')
                return redirect(request.META['HTTP_REFERER'])
        except Exception as e:
            messages.error(request, 'Something went wrong!', extra_tags='error-create-organization')
            return redirect(request.META['HTTP_REFERER'])
    locations = Location.objects.filter(is_active=True).order_by('name')
    data = {
        'locations':locations,
        'page_':'Create Organization',
        'sub_menu':'Address',
        'sub_menu2':'Organization'
    }
    return render(request, 'front-end/organization/create-organization.html', data)


def organizationList(request):
    organizations = Organization.objects.all().order_by('name')
    data = {
        'organizations':organizations,
        'page_':'Organization List',
        'sub_menu':'Address',
        'sub_menu2':'Organization'
    }
    return render(request, 'front-end/organization/organization-list.html', data)


def editOrganization(request, organizationId=0):
    if request.method == "POST":
        locations = request.POST.getlist('location-id')
        if len(locations) == 0:
            messages.error(request, 'Location is mandatory!', extra_tags='error-edit-organization')
            return redirect(request.META['HTTP_REFERER'])
        locationIds = [int(id) for id in locations]
        organizationId = request.POST.get('organization-id').strip()
        if organizationId == '':
            messages.error(request, 'Invalid input!', extra_tags='error-edit-organization')
            return redirect(request.META['HTTP_REFERER'])
        name = request.POST.get('organization-name').strip()
        if name == '':
            messages.error(request, 'Invalid input!', extra_tags='error-edit-organization')
            return redirect(request.META['HTTP_REFERER'])
        isActive = request.POST.get('is-active').strip()
        if isActive == '0':
            isActive = False
        elif isActive == '1':
            isActive = True
        else:
            messages.error(request, 'Invalid input!', extra_tags='error-edit-organization')
            return redirect(request.META['HTTP_REFERER'])
    organization = Organization.objects.get(id=organizationId)
    if request.method == 'GET':
        locations = Location.objects.filter(is_active=True).order_by('name')
        selectedLocations = organization.location.all()
        selectedLocationsArr = [location.id for location in selectedLocations]
        data = {
            'locations':locations,
            'selected_locations':selectedLocationsArr,
            'organization':organization,
            'page_':'Edit Organization',
            'sub_menu':'Address',
            'sub_menu2':'Organization'
        }
        return render(request, 'front-end/organization/edit-organization.html', data)
    try:
        with transaction.atomic():
            organization.location.set(locationIds)
            organization.name = name
            organization.is_active = isActive
            organization.save()
            messages.success(request, 'Successfully edited organization', extra_tags='success-edit-organization')
            return redirect(request.META['HTTP_REFERER'])
    except Exception as e:
        messages.success(request, 'Something went wrong!', extra_tags='error-edit-organization')
        return redirect(request.META['HTTP_REFERER'])