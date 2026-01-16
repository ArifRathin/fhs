from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import FrontPage, CustomerReview, Team
from django.contrib import messages
from account.models import User
from notification.models import Notification
# Create your views here.
def updateFrontPage(request):
    frontPage = FrontPage.objects.all().first()
    if request.method == 'POST':
        logo = request.FILES.get('logo')
        bannerImage = request.FILES.get('banner-image')
        contactEmail = request.POST.get('contact-email').strip()
        contactPhone = request.POST.get('contact-phone').strip()
        contactAddress = request.POST.get('contact-address').strip()
        aboutUs = request.POST.get('about-us').strip()
        
        try:
            if frontPage:
                if logo:
                    frontPage.logo = logo
                if bannerImage:
                    frontPage.banner_image = bannerImage
                if contactEmail != '':
                    frontPage.contact_email = contactEmail
                if contactPhone != '':
                    frontPage.contact_phone = contactPhone
                if contactAddress != '':
                    frontPage.contact_address = contactAddress
                if aboutUs != '':
                    frontPage.about_us = aboutUs
                frontPage.save()
            else:
                frontPage = FrontPage.objects.create(logo=logo, banner_image=bannerImage, contact_email=contactEmail, contact_phone = contactPhone, contact_address = contactAddress, about_us = aboutUs)
            messages.success(request, 'Successfully updated.', extra_tags='success-update-fp')
        except:
            messages.success(request, 'Something went wrong!', extra_tags='error-update-fp')
        return redirect(request.META['HTTP_REFERER'])
    
    elif request.method == 'GET':
        notifications = Notification.objects.filter(notif_for_id=request.user.id).order_by('-id')
        page_ = 'Update Front Page'
        sub_menu = 'Setting'
        data = {
            'notifications':notifications,
            'page_':page_,
            'sub_menu':sub_menu,
            'front_page':frontPage
        }
        return render(request, 'admin/update-front-page.html', data)
    

def createCustomerReview(request):
    if request.method == 'POST':
        customer = None
        if request.user.is_authenticated:
            customer = request.user
        customerName = request.POST.get('customer-name').strip()
        review = request.POST.get('review').strip()
        try:
            CustomerReview.objects.create(customer=customer, customer_name=customerName, review=review)
            messages.success(request, 'Successfully recorded your review.', extra_tags='success-create-review')
        except Exception as e:
            messages.error(request, 'Something went wrong!', extra_tags='error-create-review')    
        return redirect(request.META['HTTP_REFERER'])

    # notifications = Notification.objects.filter(notif_for_id=request.user.id).order_by('-id')
    frontPage = FrontPage.objects.all().first()
    page_ = 'Customer Review'
    data = {
        # 'notifications':notifications,
        'page_':page_,
        'front_page':frontPage
    }
    return render(request, 'base-front-end/enduser/add-customer-review.html', data)


def customerReviews(request):
    notifications = Notification.objects.filter(notif_for_id=request.user.id).order_by('-id')
    customerReviews = CustomerReview.objects.all()
    page_ = 'Customer Reviews'
    sub_menu = 'Setting'
    data={
        'notifications':notifications,
        'page_':page_,
        'sub_menu':sub_menu,
        'customer_reviews':customerReviews
    }
    return render(request, 'admin/customer-reviews.html', data)


def updateReviewStatus(request, reviewId):
    customerReview = CustomerReview.objects.get(id=reviewId)
    reviewStatus = customerReview.is_published
    customerReview.is_published = not reviewStatus
    customerReview.save()
    return redirect(request.META['HTTP_REFERER'])

def addTeamMember(request):
    if request.method == 'POST':
        memberId = request.POST.get('member-id')
        member = User.objects.get(id=memberId)
        memberImage = request.FILES.get('member-image')
        designation = request.POST.get('designation').strip()
        details = request.POST.get('details').strip()
        isPublished = request.POST.get('is-published')
        if isPublished == '0':
            isPublished = False
        else:
            isPublished = True
        try:
            team = Team.objects.create(member = member, designation = designation, details = details, is_published = isPublished)
            if memberImage != None:
                team.member_image = memberImage
                team.save()
            messages.success(request, 'Successfully added team member.', extra_tags='success-add-member')
        except:
            messages.error(request, 'Something went wrong!', extra_tags='error-add-member')
        return redirect(request.META['HTTP_REFERER'])
    notifications = Notification.objects.filter(notif_for_id=request.user.id).order_by('-id')
    members = User.objects.filter(is_admin=True, member__isnull=True)
    page_ = 'Add team member'
    sub_menu = 'Setting'
    data = {
        'notifications':notifications,
        'page_':page_,
        'sub_menu':sub_menu,
        'members':members
    }
    return render(request, 'admin/add-team-members.html', data)


def teamMembers(request):
    notifications = Notification.objects.filter(notif_for_id=request.user.id).order_by('-id')
    teamMembers = Team.objects.all()
    page_ = 'Team Members'
    sub_menu = 'Setting'
    data = {
        'notifications':notifications,
        'page_':page_,
        'sub_menu':sub_menu,
        'team_members':teamMembers
    }
    return render(request, 'admin/team-members.html', data)


def updateTeamMember(request, memberId=0):
    if request.method == 'POST':
        memberId = request.POST.get('member-id')
        memberUserId = request.POST.get('member-user-id')
        memberImage = request.FILES.get('member-image')
        designation = request.POST.get('designation').strip()
        details = request.POST.get('details').strip()
        isPublished = request.POST.get('is-published')
        if isPublished == '0':
            isPublished = False
        else:
            isPublished = True
    member = Team.objects.get(id=memberId)
    if request.method == 'GET':
        notifications = Notification.objects.filter(notif_for_id=request.user.id).order_by('-id')
        members = User.objects.filter(is_admin=True, member__isnull=True)
        page_='Update Member'
        sub_menu='Setting'
        data = {
            'notifications':notifications,
            'page_':page_,
            'sub_menu':sub_menu,
            'member':member,
            'members':members
        }
        return render(request, 'admin/update-team-members.html', data)
    memberUser = User.objects.get(id=memberUserId)
    member.member = memberUser
    if memberImage != None:
        member.member_image = memberImage
    if details != '':
        member.details = details
    member.designation = designation
    member.is_published = isPublished
    try:
        member.save()
        messages.success(request, 'Successfully updated member.', extra_tags='success-update-member')
    except:
        messages.error(request, 'Something went wrong!', extra_tags='error-update-member')
    return redirect(request.META['HTTP_REFERER'])