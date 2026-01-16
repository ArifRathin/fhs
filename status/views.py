# from django.shortcuts import render, HttpResponse, redirect
# from .models import Status
# # Create your views here.
# def createStatus(request):
#     if request.method == 'POST':
#         status = request.POST.get('status').strip()
#         isActive = request.POST.get('is-active')
#         if isActive == '1':
#             isActive = True
#         else:
#             isActive = False
#         try:
#             Status.objects.create(status=status,is_active=isActive)
#             return HttpResponse('Successfully created status!')
#         except:
#             return HttpResponse('Something went wrong!')
#     return render(request, 'front-end/create-status.html')


# def statusList(request):
#     statuses = Status.objects.all()
#     data = {
#         'statuses':statuses
#     }
#     return render(request, 'front-end/status-list.html', data)


# def editStatus(request, statusId=0):
#     if request.method == 'POST':
#         statusId = request.POST.get('status-id')
#         status = request.POST.get('status').strip()
#         isActive = request.POST.get('is-active')
#         if isActive == '1':
#             isActive = True
#         else:
#             isActive = False
#     reportStatus = Status.objects.get(id = statusId)
#     if request.method == 'GET':
#         data = {
#             'status':reportStatus
#         }
#         return render(request, 'front-end/edit-status.html', data)
#     reportStatus.status = status
#     reportStatus.is_active = isActive
#     reportStatus.save()
#     return redirect(request.META['HTTP_REFERER'])


# def deleteStatus(request):
#     statusId = request.POST.get('status-id')
#     status = Status.objects.filter(id=statusId).get()
#     try:
#         status.delete()
#         return HttpResponse('Successfully deleted the status.')
#     except:
#         return HttpResponse('Something went wrong!')