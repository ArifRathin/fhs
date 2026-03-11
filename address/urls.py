from django.urls import path
from . import views

urlpatterns = [
    # Location URLs
    path('create-location/', views.createLocation, name='create-location'),
    path('location-list/', views.locationList, name='location-list'),
    path('edit-location/', views.editLocation, name='edit-location'),
    path('edit-location/<int:locationId>', views.editLocation, name='edit-location'),
    path('delete-location/<int:locationId>', views.deleteLocation, name="delete-location"),

    # Organization URLs
    path('create-organization/', views.createOrganization, name='create-organization'),
    path('organization-list/', views.organizationList, name='organization-list'),
    path('edit-organization/', views.editOrganization, name='edit-organization'),
    path('edit-organization/<int:organizationId>', views.editOrganization, name='edit-organization'),
    path('delete-organization/<int:organizationId>', views.deleteOrganization, name="delete-organization")
]