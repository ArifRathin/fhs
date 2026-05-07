from django.shortcuts import render, redirect
from fault_report.models import FaultReport
from quotation.models import Quotation
from .models import WorkerHistory
from notification.models import Notification
from django.db import transaction
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse

def createWorkerHistory(request, workerId=0):
    if request.method == 'POST':
        workerId = request.POST.get('worker-id').strip()
        jobNumber = request.POST.get('job-number').strip()
        poNumber = request.POST.get('po-number').strip()
        ref = request.POST.get('ref').strip()
        charge = request.POST.get('charge').strip()
        dateCompleted = request.POST.get('date-completed').strip()
        signedBy = request.POST.get('signed-by').strip()
        note = request.POST.get('note').strip()
        try:
            with transaction.atomic():
                WorkerHistory.objects.create(worker_id=workerId, job_number=jobNumber, po_number=poNumber, ref=ref, charge=charge, date_completed=dateCompleted, signed_by=signedBy, note=note)
                messages.success(request, 'Worker history added successfully.', extra_tags='success-create-workerhistory')
                return redirect(request.META['HTTP_REFERER'])
        except Exception as e:
            messages.error(request, 'Something went wrong!', extra_tags='error-create-workerhistory')
            return redirect(request.META['HTTP_REFERER'])
    notifications = Notification.objects.filter(is_opened=False, notif_for_id=request.user.id).order_by('-id')
    jobNumbers = FaultReport.objects.filter(job_number__isnull=False).values_list('job_number', flat=True)
    data = {
        'notifications':notifications,
        'worker_id':workerId,
        'job_numbers':jobNumbers,
        'page_':'Add Worker History',
        'sub_menu':'Contractor'
    }
    return render(request, 'worker_history/create-workerhistory.html', data)


def workerHistoryList(request, workerId):
    histories = WorkerHistory.objects.filter(worker_id=workerId)
    pages = Paginator(histories, 10)
    pageNumber = request.GET.get('page')
    historyList = pages.get_page(pageNumber)

    notifications = Notification.objects.filter(is_opened=False, notif_for_id=request.user.id).order_by('-id')
    data = {
        'notifications':notifications,
        'history_list':historyList,
        'page_':'Worker History',
        'sub_menu':'Contractor'
    }
    return render(request, 'worker_history/workerhistory-list.html', data)


def editWorkerHistory(request, historyId=0):
    if request.method == 'POST':
        historyId = request.POST.get('history-id').strip()
        jobNumber = request.POST.get('job-number').strip()
        poNumber = request.POST.get('po-number').strip()
        ref = request.POST.get('ref').strip()
        charge = request.POST.get('charge').strip()
        dateCompleted = request.POST.get('date-completed').strip()
        signedBy = request.POST.get('signed-by').strip()
        note = request.POST.get('note').strip()
    history = WorkerHistory.objects.filter(id=historyId).first()
    if history:
        if request.method == 'GET':
            notifications = Notification.objects.filter(is_opened=False, notif_for_id=request.user.id).order_by('-id')
            jobNumbers = FaultReport.objects.filter(job_number__isnull=False).values_list('job_number', flat=True)
            data = {
                'notifications':notifications,
                'history':history,
                'job_numbers':jobNumbers,
                'page_':'Worker History',
                'sub_menu':'Contractor'
            }
            return render(request, 'worker_history/edit-worker-history.html', data)
        else:
            try:
                with transaction.atomic():
                    history.job_number = jobNumber
                    history.po_number = poNumber
                    history.ref = ref
                    history.charge = charge
                    history.date_completed = dateCompleted
                    history.signed_by = signedBy
                    history.note = note

                    history.save()
                    messages.success(request, 'Successfully edited the history.', extra_tags='success-edit-workerhistory')
                    return redirect(request.META['HTTP_REFERER'])
            except Exception as e:
                messages.error(request, 'Something went wrong!', extra_tags='error-edit-workerhistory')
                return redirect(request.META['HTTP_REFERER'])
    else:
        messages.error(request, "This history doesn't exist!", extra_tags='error-workerhistory-list')
        return redirect(request.META['HTTP_REFERER'])


def deleteWorkerHistory(request, historyId):
    try:
        history = WorkerHistory.objects.filter(id=historyId).first()
        if history:
            history.delete()
            messages.success(request, 'Successfully deleted the worker history', extra_tags='success-workerhistory-list')
            return redirect(request.META['HTTP_REFERER'])
        else:
            messages.success(request, "History doesn't exist!", extra_tags='error-workerhistory-list')
            return redirect(request.META['HTTP_REFERER'])
    except Exception as e:
        messages.success(request, "Something went wrong!", extra_tags='error-workerhistory-list')
        return redirect(request.META['HTTP_REFERER'])
    

def getPORefNumber(request):
    jobNumber=request.GET.get('jobNumber')
    poNumber = None
    quoteRef = None
    result = FaultReport.objects.filter(job_number=jobNumber).values('id', 'po_number').first()
    if result:
        poNumber = result['po_number']
        ref = Quotation.objects.filter(fault_report_id=result['id'], approval_status='QA').values_list('quote_ref_num', flat=True).first()
        if ref:
            quoteRef = ref
    return JsonResponse({'po_number':poNumber, 'ref':quoteRef})