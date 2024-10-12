from django.urls import path, include
from django.http import JsonResponse

urlpatterns = [
    path('', include("users.urls")),
]
