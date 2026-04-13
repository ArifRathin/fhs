from django.urls import path
from property import views_property, views_item

urlpatterns = [
    # Property URLs
    path('create-property/', views_property.createProperty, name='create-property'),
    path('property-list/', views_property.propertyList, name='property-list'),
    path('edit-property/<int:propertyId>', views_property.editProperty, name='edit-property'),
    path('edit-property/', views_property.editProperty, name='edit-property'),
    path('delete-property/<int:propertyId>', views_property.deleteProperty, name='delete-property'),


    # Item URLs
    path('create-item/', views_item.createItem, name='create-item'),
    path('create-item/<int:propertyId>', views_item.createItem, name='create-item'),
    path('item-list/<int:propertyId>/<int:category>/<str:condition>/', views_item.itemList, name='item-list'),
    path('edit-item/<int:itemId>', views_item.editItem, name='edit-item'),
    path('edit-item/', views_item.editItem, name='edit-item'),
    path('delete-item/<int:itemId>', views_item.deleteItem, name='delete-item')
]