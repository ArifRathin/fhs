from django.urls import path
from . import views_admin, views_technician, views_enduser
from fault_report import views as views_fault_reports

urlpatterns = [
    path('home/', views_admin.home, name='home'),
    # Admin URLs
    path('create-admin/', views_admin.createAdmin, name='create-admin'),
    path('create-admin-internal/<str:type>', views_admin.createAdmin, name='create-admin-internal'),
    path('edit-admin/<int:adminId>', views_admin.editAdmin, name='edit-admin'),
    path('edit-admin/', views_admin.editAdmin, name='edit-admin'),
    path('admin-list/', views_admin.adminList, name='admin-list'),
    path('login-user/', views_admin.loginUser, name='login-user'),
    path('logout-admin/', views_admin.logoutAdmin, name='logout-admin'),
    path('permissions-admin/<int:adminId>', views_admin.permissionList, name='permissions-admin'),
    path('update-permissions-admin/', views_admin.updatePermissions, name='update-permissions-admin'),

    # Technician URLs
    path('create-technician/', views_technician.createTechnician, name='create-technician'),
    path('technician-list/', views_technician.technicianList, name='technician-list'),
    path('edit-technician/<int:technicianId>', views_technician.editTechnician, name='edit-technician'),
    path('edit-technician/', views_technician.editTechnician, name='edit-technician'),

    # End-user URLs
    path('create-enduser/', views_enduser.createEndUser, name='create-enduser'),
    path('send-change-password-link/', views_enduser.sendChangePasswordLink, name='send-change-password-link'),
    path('change-password/<str:code>', views_enduser.changePassword, name='change-password'),
    path('change-password/', views_enduser.changePassword, name='change-password'),
    # Fault Reports URLs
    path('fault-reports/', views_fault_reports.faultReportList, name='fault-reports')
]