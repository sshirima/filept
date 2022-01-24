from django.urls import path
from django.conf.urls.static import static
from django.conf import settings


from . import views

urlpatterns = [
    path('', views.userreviews, name='userreviews'),
    path('upload-system-logs/<str:system_name>', views.upload_system_logs, name='upload_system_logs'),
    path('download-file/<str:filename>', views.download_file, name='download_file'),
    path('data-import', views.data_import, name='data_import'),
    path('data-import-create/<str:system_name>', views.data_import_create, name='data_import_create'),
    path('accounts', views.SystemAccountListView.as_view(), name='accounts_view'),
]