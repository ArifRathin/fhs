from django.urls import path
from . import views
urlpatterns = [
    path('create-quotation/<int:faultReportId>', views.createQuotation, name='create-quotation'),
    path('create-quotation/', views.createQuotation, name='create-quotation'),
    path('view-quotation/<str:quoteRefNum>', views.viewQuotation, name='view-quotation'),
    path('send-quotation/<str:quoteRefNum>', views.sendQuotation, name='send-quotation'),
    path('cancel-quotation/<str:quoteRefNum>', views.cancelQuotation, name='cancel-quotation')
]