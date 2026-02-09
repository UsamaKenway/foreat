from django.urls import path
from . import views

urlpatterns = [
    path('upload/', views.upload_view, name='sales_upload'),
    path('map-columns/', views.map_columns_view, name='sales_map_columns'),
]
