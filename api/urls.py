from django.urls import path,include
from django.conf import settings
from . import views

urlpatterns = [
    path('imagemodel/',views.ImageModelAPIView.as_view()),
]