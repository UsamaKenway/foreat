from django.urls import path
from . import views

urlpatterns = [
    path('', views.competitor_dashboard, name='competitor_dashboard'),
    path('analyze/', views.run_competitor_analysis, name='run_competitor_analysis'),
]
