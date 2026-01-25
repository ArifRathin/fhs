from django.shortcuts import render
from fault_report.models import FaultReport
from account.models import User
from notification.models import Notification
from front_page.models import FrontPage, CustomerReview, Team
from django.http import JsonResponse

def home(request):
    totalCompleted = FaultReport.objects.filter(completed_at__isnull=False).count()
    uniqueCustomers = User.objects.filter(fault_report__isnull=True,is_enduser=True).count()
    totalLocations = FaultReport.objects.distinct('location').count()
    frontPage = FrontPage.objects.all().first()
    customerReviews = CustomerReview.objects.filter(is_published=True).order_by('?')[:5]
    members = Team.objects.filter(is_published=True).order_by('id')[:5]
    data = {
        'total_completed':totalCompleted,
        'unique_customers':uniqueCustomers,
        'total_locations':totalLocations,
        'front_page':frontPage,
        'customer_reviews':customerReviews,
        'members':members
    }
    return render(request, 'base-front-end/enduser/home.html', data)


def updateNotifStatus(request):
    notifId = request.GET.get('notif-id')
    try:
        Notification.objects.filter(id__lte = notifId, notif_for_id=request.user.id).update(is_opened=True)
        return JsonResponse({'success':True})
    except Exception as e:
        return JsonResponse({'success':str(e)})