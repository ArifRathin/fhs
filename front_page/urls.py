from django.urls import path
from . import views
urlpatterns = [
    path('update-front-page/', views.updateFrontPage, name='update-front-page'),
    path('create-customer-review/', views.createCustomerReview, name='create-customer-review'),
    path('customer-reviews/', views.customerReviews, name='customer-reviews'),
    path('update-review-status/<int:reviewId>', views.updateReviewStatus, name='update-review-status'),
    path('add-team-member/', views.addTeamMember, name='add-team-member'),
    path('team-members/', views.teamMembers, name='team-members'),
    path('update-team-member/<int:memberId>', views.updateTeamMember, name='update-team-member'),
    path('update-team-member/', views.updateTeamMember, name='update-team-member')

]