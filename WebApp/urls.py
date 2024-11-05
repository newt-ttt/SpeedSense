from django.urls import path
from . import views

urlpatterns = [
    path("ping/", views.ping, name="ping"),
    path("save/", views.save, name="save"),
    path("", views.index, name="index"),
    path("<str:resource>/", views.index, name="index")
]
