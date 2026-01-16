"""
URL configuration for fhs project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='landing-page'),
    path('update-notif-status/', views.updateNotifStatus, name='update-notif-status'),
    path('user-management-area/', include('account.urls')),
    path('user-management-area/', include('job.urls')),
    # path('user-management-area/', include('priority_level.urls')),
    # path('user-management-area/', include('status.urls')),
    path('user-management-area/', include('quotation.urls')),
    path('front-area/', include('fault_report.urls')),
    path('front-page/', include('front_page.urls'))
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)