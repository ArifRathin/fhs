from django.shortcuts import render, HttpResponse, redirect
from .models import Job
from notification.models import Notification
from django.contrib.auth.decorators import login_required
from django.contrib import messages
# Create your views here.
@login_required(login_url='login-user')
def createJob(request):
    if request.user.is_admin and request.user.has_perm('job.add_job'):
        if request.method == 'POST':
            title = request.POST.get('title').strip()
            description = request.POST.get('description').strip()
            if description == '':
                description = None
            isActive = request.POST.get('is-active')
            if isActive == '1':
                isActive = True
            else:
                isActive = False
            try:
                Job.objects.create(title=title, description=description, is_active=isActive)
                messages.success(request, 'Successfully created job', extra_tags='success-create-job')
            except Exception as e:
                messages.error(request, 'Something went wrong!', extra_tags='error-create-job')
            return redirect(request.META['HTTP_REFERER'])
        notifications = Notification.objects.filter(notif_for_id=request.user.id).order_by('-id')
        sub_menu = 'Job'
        page_ = 'Create Job'
        data = {
            'notifications':notifications,
            'sub_menu':sub_menu,
            'page_':page_
        }
        return render(request, 'front-end/create-job.html', data)
    else:
        return render(request, 'no-permission.html')


@login_required(login_url='login-user')
def jobList(request):
    if request.user.is_admin and request.user.has_perm('job.view_job'):
        jobs = Job.objects.all()
        notifications = Notification.objects.filter(notif_for_id=request.user.id).order_by('-id')
        sub_menu = 'Job'
        page_ = 'Job List'
        data = {
            'notifications':notifications,
            'jobs':jobs,
            'sub_menu':sub_menu,
            'page_':page_
        }
        return render(request, 'front-end/job-list.html', data)
    else:
        return render(request, 'no-permission.html')


def editJob(request, jobId=0):
    if request.user.is_admin and request.user.has_perm('job.change_job'):
        try:
            if request.method == 'POST':
                jobId = request.POST.get('job-id')
                title = request.POST.get('title').strip()
                description = request.POST.get('description').strip()
                if description == '':
                    description = None
                isActive = request.POST.get('is-active')
                if isActive == '1':
                    isActive = True
                else:
                    isActive = False
            job = Job.objects.filter(id=jobId).get()
            if request.method == 'GET':
                data={
                    'job':job
                }
                return render(request, 'front-end/edit-job.html', data)
            job.title = title
            job.description = description
            job.is_active = isActive
            job.save()
            messages.success(request, 'Successfully updated the job.', extra_tags='success-update-job')
        except:
            messages.success(request, 'Something went wrong!', extra_tags='error-update-job')
        return redirect(request.META['HTTP_REFERER'])
    else:
        return render(request, 'no-permission.html')


def deleteJob(request):
    jobId = request.POST.get('job-id')
    job = Job.objects.filter(id=jobId).get()
    try:
        job.delete()
        return HttpResponse('Successfully deleted the job.')
    except:
        return HttpResponse('Something went wrong!')