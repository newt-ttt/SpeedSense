from django.urls import path
from . import views

urlpatterns = [
    path("ping/", views.ping, name="ping"),
    path("save/", views.save, name="save"),
    path("logopage/", views.logo, name="logo"),
    path("", views.index, name="index"),
]
