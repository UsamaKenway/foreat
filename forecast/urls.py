from django.urls import path
from . import views

urlpatterns = [
    path('', views.training_hub, name='training_hub'),
    path('train/', views.train_model, name='train_model'),
]
