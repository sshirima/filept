from django.urls import path
from django.conf.urls.static import static
from django.conf import settings

from . import views

urlpatterns = [
    path('', views.userreviews, name='userreviews'),
    path('create/<str:nodename>', views.userreviews_create, name='userreviews_create'),
    path('download-file/<str:filename>', views.download_file, name='download_file'),
    path('data-import', views.data_import, name='data_import'),
    path('data-import-create', views.data_import_create, name='data_import_create'),
]