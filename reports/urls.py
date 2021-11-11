from django.urls import path

from . import views

urlpatterns = [
    path('', views.reports, name='reports'),
    path('create/<str:reportname>', views.reports_create, name='reports_create'),
]