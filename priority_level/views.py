# from django.shortcuts import render, HttpResponse, redirect
# from .models import PriorityLevel
# # Create your views here.
# def createPriorityLevel(request):
#     if request.method == 'POST':
#         level = request.POST.get('level')
#         isActive = request.POST.get('priority-level')
#         if isActive == '1':
#             isActive = True
#         else:
#             isActive = False
#         try:
#             PriorityLevel.objects.create(level=level, is_active=isActive)
#             return HttpResponse('Successfully created priority level!')
#         except:
#             return HttpResponse('Something went wrong!')
#     return render(request, 'front-end/create-priority-level.html')


# def priorityLevelList(request):
#     priorityLevel = PriorityLevel.objects.all()
#     data = {
#         'priority_levels':priorityLevel
#     }
#     return render(request, 'front-end/priority-level-list.html', data)


# def editPriorityLevel(request, levelId=0):
#     if request.method == 'POST':
#         levelId = request.POST.get('level-id')
#         level = request.POST.get('level').strip()
#         isActive = request.POST.get('is-active')
#         if isActive == '1':
#             isActive = True
#         else:
#             isActive = '0'
#     priorityLevel = PriorityLevel.objects.filter(id=levelId).get()
#     if request.method == 'GET':
#         data = {
#             'level':priorityLevel
#         }
#         return render(request, 'front-end/edit-priority-level.html', data)
#     priorityLevel.level = level
#     priorityLevel.is_active = isActive
#     priorityLevel.save()
#     return redirect(request.META['HTTP_REFERER'])


# def deletePriorityLevel(request):
#     levelId = request.POST.get('level-id')
#     level = PriorityLevel.objects.filter(id=levelId).get()
#     try:
#         level.delete()
#         return HttpResponse('Successfully deleted the priority level.')
#     except:
#         return HttpResponse('Something went wrong!')