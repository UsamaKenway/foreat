from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Competitor, CompetitorTraffic, CompetitorDeal
from .services import CompetitorAgent
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from sales.models import SalesData
from django.db.models import Sum

@login_required
def competitor_dashboard(request):
    competitors = Competitor.objects.all()
    
    # Traffic Battle Chart
    # Compare own sales (quantity) with competitor traffic scores
    own_sales = SalesData.objects.values('transaction_date').annotate(
        total_qty=Sum('quantity_sold')
    ).order_by('transaction_date')
    
    chart_traffic = ""
    if own_sales.exists():
        df_own = pd.DataFrame(own_sales)
        df_own['date'] = df_own['transaction_date'].dt.date
        df_own = df_own.groupby('date')['total_qty'].sum().reset_index()
        
        fig = go.Figure()
        # My Sales
        fig.add_trace(go.Scatter(
            x=df_own['date'], 
            y=df_own['total_qty'], 
            name='My Sales (Qty)', 
            line=dict(color='#2DD4BF', width=4)
        ))
        
        # Competitor Traffic
        for comp in competitors:
            traffic_data = list(comp.traffic_logs.all().order_by('date').values('date', 'traffic_score'))
            if traffic_data:
                df_comp = pd.DataFrame(traffic_data)
                fig.add_trace(go.Scatter(
                    x=df_comp['date'], 
                    y=df_comp['traffic_score'], 
                    name=f'{comp.name} Traffic', 
                    line=dict(dash='dot')
                ))
        
        fig.update_layout(
            title="Traffic Battle: My Sales vs Competitors", 
            template="plotly_white",
            xaxis_title="Date",
            yaxis_title="Volume / Score"
        )
        chart_traffic = fig.to_html(full_html=False)

    # Deal Impact (Scatter Plot)
    chart_deals = ""
    deals = CompetitorDeal.objects.select_related('competitor').all()
    if deals.exists():
        deal_data = []
        for d in deals:
            deal_data.append({
                'Competitor': d.competitor.name,
                'Deal': d.deal_title,
                'Impact Score': d.impact_on_traffic,
                'Date': d.date_observed
            })
        df_deals = pd.DataFrame(deal_data)
        fig_deals = px.scatter(
            df_deals, x='Date', y='Impact Score', color='Competitor', 
            hover_data=['Deal'], title="Competitor Deal Impact Analysis",
            template="plotly_white", color_discrete_sequence=px.colors.qualitative.Antique
        )
        chart_deals = fig_deals.to_html(full_html=False)

    context = {
        'competitors': competitors,
        'chart_traffic': chart_traffic,
        'chart_deals': chart_deals,
        'deals': deals[:10]
    }
    return render(request, 'competitor_intel/dashboard.html', context)

@login_required
def run_competitor_analysis(request):
    if request.method == 'POST':
        location = request.POST.get('location', 'Downtown')
        agent = CompetitorAgent()
        agent.analyze_location(location)
    return redirect('competitor_dashboard')
