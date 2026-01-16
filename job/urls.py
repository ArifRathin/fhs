from django.urls import path
from . import views

urlpatterns = [
    path('create-job/', views.createJob, name='create-job'),
    path('job-list/', views.jobList, name='job-list'),
    path('edit-job/<int:jobId>', views.editJob, name='edit-job'),
    path('edit-job/', views.editJob, name='edit-job')
]