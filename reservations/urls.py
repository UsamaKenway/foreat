from django.urls import path
from . import views

urlpatterns = [
    path('', views.reservation_dashboard, name='reservation_dashboard'),
    path('train/', views.train_noshow_model, name='train_noshow_model'),
]
