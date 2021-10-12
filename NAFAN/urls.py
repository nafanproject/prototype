from django.urls import path
from NAFAN import views

urlpatterns = [
    path("", views.home, name="home"),
    path("newToNAFAN/", views.newToNAFAN, name="newToNAFAN"),
]