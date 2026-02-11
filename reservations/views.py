from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import ReservationSignal, NoShowTrainingRun
import plotly.express as px
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
import joblib
import os
from django.conf import settings

@login_required
def reservation_dashboard(request):
    reservations = ReservationSignal.objects.all().order_by('target_date')
    recent_training = NoShowTrainingRun.objects.last()
    
    if not reservations.exists():
        return render(request, 'reservations/dashboard.html', {'no_data': True})
    
    data = []
    for r in reservations:
        no_show_count = max(0, r.booking_count - r.actual_arrivals)
        no_show_rate = (no_show_count / r.booking_count * 100) if r.booking_count > 0 else 0
        data.append({
            'Date': r.target_date,
            'Bookings': r.booking_count,
            'Actuals': r.actual_arrivals,
            'No-Show Rate (%)': no_show_rate
        })
    
    df = pd.DataFrame(data)
    
    # Chart 1: Bookings vs Actuals
    fig1 = px.bar(df, x='Date', y=['Bookings', 'Actuals'], barmode='group', 
                  title="Bookings vs Actual Arrivals",
                  template="plotly_white",
                  color_discrete_sequence=['#2DD4BF', '#14B8A6'])
    
    # Chart 2: No-Show Rate over time
    fig2 = px.line(df, x='Date', y='No-Show Rate (%)', title="No-Show Rate Trend",
                   template="plotly_white",
                   color_discrete_sequence=['#F43F5E'])

    context = {
        'chart_bookings': fig1.to_html(full_html=False),
        'chart_noshow': fig2.to_html(full_html=False),
        'reservations': reservations.order_by('-target_date')[:10],
        'recent_training': recent_training
    }
    return render(request, 'reservations/dashboard.html', context)

@login_required
def train_noshow_model(request):
    reservations = ReservationSignal.objects.all()
    if reservations.count() < 10:
        messages.error(request, "Not enough data to train model. Need at least 10 records.")
        return redirect('reservation_dashboard')
        
    data = []
    for r in reservations:
        data.append({
            'day_of_week': r.target_date.weekday(),
            'booking_count': r.booking_count,
            'party_size': r.party_size_total,
            'target': r.booking_count - r.actual_arrivals
        })
        
    df = pd.DataFrame(data)
    X = df[['day_of_week', 'booking_count', 'party_size']]
    y = df['target']
    
    model = RandomForestRegressor(n_estimators=100)
    model.fit(X, y)
    
    # Save model
    model_dir = os.path.join(settings.MEDIA_ROOT, 'models')
    os.makedirs(model_dir, exist_ok=True)
    model_path = os.path.join(model_dir, 'noshow_model.pkl')
    joblib.dump(model, model_path)
    
    NoShowTrainingRun.objects.create(
        mae=0.0, # Simplified
        model_path=model_path
    )
    
    messages.success(request, "No-Show prediction model trained successfully!")
    return redirect('reservation_dashboard')
