from django.shortcuts import render, redirect
from django.http import HttpResponse
from notification.models import Notification
from job.models import Job
from property.models import Property, Item, ItemCondition, ItemPhoto
from django.contrib import messages
from django.db import transaction
from fhs.image_processor import processImage

def createItem(request, propertyId=0):
    if request.method == 'POST':
        propertyId = request.POST.get('property-id')
        if not Property.objects.filter(id=propertyId).exists():
            messages.error(request, "Property doesn't exist!", extra_tags='error-create-item')
            return redirect(request.META['HTTP_REFERER'])
        name = request.POST.get('name').strip()
        if name == '':
            messages.error(request, "Name is mandatory", extra_tags='error-create-item')
            return redirect(request.META['HTTP_REFERER'])
        notes = request.POST.get('description').strip()
        category = request.POST.get('category').strip()
        if not Job.objects.filter(id=category).exists():
            messages.error(request, "Invalid category!", extra_tags='error-create-item')
            return redirect(request.META['HTTP_REFERER'])
        condition = request.POST.get('condition').strip()
        if condition not in ItemCondition:
            messages.error(request, "Invalid condition!", extra_tags='error-create-item')
            return redirect(request.META['HTTP_REFERER'])
        dateRecorded = request.POST.get('date-recorded').strip()
        if dateRecorded == '':
            messages.error(request, "Invalid date!", extra_tags='error-create-item')
            return redirect(request.META['HTTP_REFERER'])
        images = request.FILES.getlist('photos')
        try:
            with transaction.atomic():
                item = Item.objects.create(property_id=propertyId, name=name, notes=notes, category_id=category, date_recorded=dateRecorded)
                imgArr = []
                for image in images:
                    image = processImage(image)
                    imgArr.append(ItemPhoto(item=item, image=image))
                ItemPhoto.objects.bulk_create(imgArr)
                messages.success(request, "Successfully created the item.", extra_tags='success-create-item')
                return redirect(request.META['HTTP_REFERER'])
        except Exception as e:
            messages.error(request, str(e), extra_tags='error-create-item')
            return redirect(request.META['HTTP_REFERER'])

    notifications = Notification.objects.filter(is_opened=False, notif_for_id=request.user.id).order_by('-id')
    categories = Job.objects.all()
    data = {
        'property_id':propertyId,
        'notifications':notifications,
        'categories':categories,
        'conditions':ItemCondition.choices,
        'page_':'Create Item',
        'sub_menu':'Properties'
    }
    return render(request, 'item/create-item.html', data)

def itemList(request, propertyId, category=0, condition='ALL'):
    notifications = Notification.objects.filter(is_opened=False, notif_for_id=request.user.id).order_by('-id')
    categories = Job.objects.all()
    category_name = 'All Categories'
    condition_name = 'All Conditions'
    if category != 0 or condition != 'ALL':
        if category != 0 and condition == 'ALL':
            items = Item.objects.filter(property_id=propertyId, category_id=category)
            cat = Job.objects.filter(id=category).first()
            if cat:
                category_name = cat.title
            else:
                messages.error(request, 'Invalid category!', 'error-filter-item')
                return redirect(request.META['HTTP_REFERER'])
        elif category == 0 and condition != 'ALL':
            items = Item.objects.filter(property_id=propertyId, condition=condition)
            if condition in ItemCondition:
                condition_name = ItemCondition(condition).label
            else:
                messages.error(request, 'Invalid condition!', 'error-filter-item')
                return redirect(request.META['HTTP_REFERER'])
        elif category != 0 and condition != 'ALL':
            cat = Job.objects.filter(id=category).first()
            if category:
                category_name = cat.title
            else:
                messages.error(request, 'Invalid category!', 'error-filter-item')
                return redirect(request.META['HTTP_REFERER'])
            if condition in ItemCondition:
                condition_name = ItemCondition(condition).label
            else:
                messages.error(request, 'Invalid condition!', 'error-filter-item')
                return redirect(request.META['HTTP_REFERER'])
            items = Item.objects.filter(property_id=propertyId, category_id=category, condition=condition)
    else:
        items = Item.objects.filter(property_id=propertyId)
    data = {
        'notifications':notifications,
        'property_id':propertyId,
        'categories':categories,
        'category':category,
        'category_name':category_name,
        'items':items,
        'conditions':ItemCondition.choices,
        'condition':condition,
        'condition_name':condition_name,
        'page_':'Item List',
        'sub_menu':'Properties'
    }

    return render(request, 'item/item-list.html', data)


def editItem(request, itemId=0):
    if request.method == 'POST':
        itemId = request.POST.get('item-id')
        if not Item.objects.filter(id=itemId).exists():
            messages.error(request, "Item doesn't exist.", extra_tags='error-edit-item')
            return redirect(request.META['HTTP_REFERER'])
        name = request.POST.get('name').strip()
        if name == '':
            messages.error(request, "Name is mandatory.", extra_tags='error-edit-item')
            return redirect(request.META['HTTP_REFERER'])
        notes = request.POST.get('description').strip()
        category = request.POST.get('category')
        condition = request.POST.get('condition')
        dateRecorded = request.POST.get('date-recorded')
        images = request.FILES.getlist('photos')
        existingImages = request.POST.getlist('existing-images')
    item = Item.objects.filter(id=itemId).first()
    if item:
        if request.method == 'GET':
            notifications = Notification.objects.filter(is_opened=False, notif_for_id=request.user.id).order_by('-id')
            categories = Job.objects.all()
            data = {
                'item':item,
                'notifications':notifications,
                'categories':categories,
                'conditions':ItemCondition.choices,
                'page_':'Edit Item',
                'sub_menu':'Properties'
            }
            return render(request, 'item/edit-item.html', data)
        else:
            try:
                with transaction.atomic():
                    item.name = name
                    item.notes = notes
                    item.category_id = category
                    item.condition = condition
                    item.date_recorded = dateRecorded
                    item.save()
                    existingImages = ItemPhoto.objects.filter(item_id=itemId).exclude(image__in=existingImages)
                    for image in existingImages:
                        image.image.delete(save=False)
                        image.delete()
                    imgArr = []
                    for image in images:
                        image = processImage(image)
                        imgArr.append(ItemPhoto(item=item, image=image))
                    ItemPhoto.objects.bulk_create(imgArr)
                    messages.success(request, "Successfully edited the item.", extra_tags='success-edit-item')
                    return redirect(request.META['HTTP_REFERER'])
            except Exception as e:
                messages.error(request, "Something went wrong!", extra_tags='error-edit-item')
                return redirect(request.META['HTTP_REFERER'])
    else:
        messages.error(request, "Item doesn't exist!", extra_tags='error-edit-item')
        return redirect(request.META['HTTP_REFERER'])


def deleteItem(request, itemId):
    item = Item.objects.filter(id=itemId).first()
    if item:
        try:
            for photo in item.photos.all():
                photo.image.delete(save=False)
                photo.delete()
            item.delete()
            messages.success(request, "Successfully edited the item.", extra_tags='success-delete-item')
            return redirect(request.META['HTTP_REFERER'])
        except Exception as e:
            messages.error(request, "Something went wrong!", extra_tags='error-delete-item')
            return redirect(request.META['HTTP_REFERER'])
