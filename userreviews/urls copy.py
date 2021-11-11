from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='homepage'),
    path('nodes', views.nodes_index, name='nodes_index'),
    path('nodes/user-review/<str:node_name>', views.user_review_generate, name='user-review'),
    path('reports', views.reports_index, name='reports_index'),

    path('data/update', views.data_update, name='data-update'),
    path('data/upload/<str:node_name>', views.data_upload, name='data-upload'),
]