from django.urls import path
from . import views
from quotation import views as views_quotation

urlpatterns = [
    path('create-fault-report/', views.createFaultReport, name='create-fault-report'),
    path('edit-fault-report/<int:faultReportId>', views.editFaultReport, name='edit-fault-report'),
    path('edit-fault-report/', views.editFaultReport, name='edit-fault-report'),
    path('delete-fault-report/<int:reportId>', views.deleteFaultReport, name='delete-fault-report'),
    path('assign-a-technician/', views.assignATechnician, name='assign-a-technician' ),
    path('view-client-quotation/<str:quoteEmailCode>', views_quotation.viewClientQuotation, name='view-client-quotation'),
    path('update-client-approval-status/<str:quoteRefNum>/<str:approvalStatus>', views_quotation.updateClientApprovalStatus, name='update-client-approval-status'),
    path('start-task/<str:jobNumber>', views.startTask, name='start-task'),
    path('pause-task/<str:jobNumber>', views.pauseTask, name='pause-task'),
    path('resume-task/<str:jobNumber>', views.resumeTask, name='resume-task'),
    path('complete-task/<str:jobNumber>', views.completeTask, name='complete-task'),
    path('fault-report-details/<str:jobNumber>', views.faultReportDetails, name='fault-report-details')
]