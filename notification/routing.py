from django.urls import re_path
from .consumers import NotificationConsumer


urlpatterns = [
    re_path(r"ws/notification/$", NotificationConsumer.as_asgi())
]