from django.urls import path
from . import views_worker, views_worker_history

urlpatterns = [
    # Worker URLs
    path('create-worker/', views_worker.createWorker, name='create-worker'),
    path('worker-list/', views_worker.workerList, name='worker-list'),
    path('delete-worker/<int:workerId>', views_worker.deleteWorker, name='delete-worker'),
    path('edit-worker/<int:workerId>', views_worker.editWorker, name='edit-worker'),
    path('edit-worker/', views_worker.editWorker, name='edit-worker'),

    # Worker history URLs
    path('create-workerhistory/', views_worker_history.createWorkerHistory, name='create-workerhistory'),
    path('create-workerhistory/<int:workerId>', views_worker_history.createWorkerHistory, name='create-workerhistory'),
    path('workerhistory-list/<int:workerId>', views_worker_history.workerHistoryList, name='workerhistory-list'),
    path('edit-workerhistory/', views_worker_history.editWorkerHistory, name='edit-workerhistory'),
    path('edit-workerhistory/<int:historyId>', views_worker_history.editWorkerHistory, name='edit-workerhistory'),
    path('delete-workerhistory/<int:historyId>', views_worker_history.deleteWorkerHistory, name='delete-workerhistory'),
    path('get-po-ref-number/', views_worker_history.getPORefNumber, name='get-po-ref-number')
]