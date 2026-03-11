from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from notification.models import Notification
from account.models import User
from .models import Location, Organization
from django.db import transaction
# Create your views here.
@permission_required('address.add_location', login_url='login-user', raise_exception=True)
def createLocation(request):
    if request.method == 'POST':
        name = request.POST.get('location-name').strip()
        if name == '' or name == None:
            messages.error(request, 'Location name is mandatory to add a location!', extra_tags='error-create-location')
            return redirect(request.META['HTTP_REFERER'])
        if Location.objects.filter(name__iexact=name).exists():
            location = Location.objects.get(name__iexact=name)
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
            with transaction.atomic():
                location = Location.objects.create(name=name, address=address, is_active=isActive)
                users = User.objects.filter(location_name__iexact=name)
                for user in users:
                    user.location_name = None
                    user.user_location.set([location.id])
                    user.save()
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


@permission_required('address.view_location', login_url='login-user', raise_exception=True)
def locationList(request):
    notifications = Notification.objects.filter(is_opened=False, notif_for_id=request.user.id).order_by('-id')
    locations = Location.objects.all().order_by('name')
    data = {
        'notifications':notifications,
        'locations':locations,
        'sub_menu':'Address',
        'sub_menu2':'Location',
        'page_':'Location List'
    }
    return render(request, 'front-end/location/location-list.html', data)


@permission_required('address.change_location', login_url='login-user', raise_exception=True)
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
    notifications = Notification.objects.filter(is_opened=False, notif_for_id=request.user.id).order_by('-id')     
    location = Location.objects.get(id=locationId)
    if request.method == 'GET':
        data = {
            'notifications':notifications,
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
    

@permission_required('address.delete_location', login_url='login-user', raise_exception=True)
def deleteLocation(request, locationId):
    try:
        Location.objects.get(id=locationId).delete()
        messages.success(request, 'Successfully deleted location.', extra_tags='success-delete-location')
        return redirect(request.META['HTTP_REFERER'])
    except Exception as e:
        messages.error(request, 'Something went wrong!', extra_tags='error-delete-location')
        return redirect(request.META['HTTP_REFERER'])


@permission_required('address.add_organization', login_url='login-user', raise_exception=True)
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
                if locations[0] == 'other':
                    locationName = request.POST.get('location-name').strip()
                    if locationName == '':
                        messages.error(request, 'Location name is invalid!', extra_tags='error-create-location')
                        return redirect(request.META['HTTP_REFERER'])
                    elif Location.objects.filter(name__iexact=locationName).exists():
                        location = Location.objects.get(name__iexact=locationName)
                    else:
                        location = Location.objects.create(name=locationName, is_active=True)
                        users = User.objects.filter(location_name__iexact=locationName)
                        for user in users:
                            user.location_name = None
                            user.user_location.set([location.id])
                            user.save()
                    locationIds = []
                    locationIds.append(location.id)
                else:
                    locationIds = [int(id) for id in locations]
                if Organization.objects.filter(name__iexact=name).exists():
                    organization = Organization.objects.get(name__iexact=name)
                    organization.location.add(*locationIds)
                    User.objects.filter(organization_name__iexact=name).update(organization_id=organization.id, organization_name=None)
                else:
                    organization = Organization.objects.create(name=name, is_active=isActive)
                    organization.location.set(locationIds)
                    User.objects.filter(organization_name__iexact=name).update(organization_id=organization.id, organization_name=None)
                messages.success(request, 'Successfully created organization', extra_tags='success-create-organization')
                return redirect(request.META['HTTP_REFERER'])
        except Exception as e:
            messages.error(request, str(e), extra_tags='error-create-organization')
            return redirect(request.META['HTTP_REFERER'])
    notifications = Notification.objects.filter(is_opened=False, notif_for_id=request.user.id).order_by('-id')
    locations = Location.objects.filter(is_active=True).order_by('name')
    data = {
        'notifications':notifications,
        'locations':locations,
        'page_':'Create Organization',
        'sub_menu':'Address',
        'sub_menu2':'Organization'
    }
    return render(request, 'front-end/organization/create-organization.html', data)


@permission_required('address.view_organization', login_url='login-user', raise_exception=True)
def organizationList(request):
    notifications = Notification.objects.filter(is_opened=False, notif_for_id=request.user.id).order_by('-id')
    organizations = Organization.objects.all().order_by('name')
    data = {
        'notifications':notifications,
        'organizations':organizations,
        'page_':'Organization List',
        'sub_menu':'Address',
        'sub_menu2':'Organization'
    }
    return render(request, 'front-end/organization/organization-list.html', data)


@permission_required('address.change_organization', login_url='login-user', raise_exception=True)
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
        notifications = Notification.objects.filter(is_opened=False, notif_for_id=request.user.id).order_by('-id')
        locations = Location.objects.filter(is_active=True).order_by('name')
        selectedLocations = organization.location.all()
        selectedLocationsArr = [location.id for location in selectedLocations]
        data = {
            'notifications':notifications,
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
    

@permission_required('address.delete_organization', login_url='login-user', raise_exception=True)
def deleteOrganization(request, organizationId):
    try:
        Organization.objects.get(id=organizationId).delete()
        messages.success(request, 'Successfully deleted organization.', extra_tags='success-delete-organization')
        return redirect(request.META['HTTP_REFERER'])
    except Exception as e:
        messages.error(request, 'Something went wrong!', extra_tags='error-delete-organization')
        return redirect(request.META['HTTP_REFERER'])