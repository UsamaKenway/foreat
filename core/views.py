from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from sales.models import SalesData
from forecast.models import TrainingRun, SalesPrediction
from django.db.models import Sum

@login_required
def dashboard(request):
    total_sales = SalesData.objects.aggregate(Sum('total_price'))['total_price__sum'] or 0
    recent_training = TrainingRun.objects.last()
    
    context = {
        'total_sales': total_sales,
        'recent_training': recent_training,
        'recent_sales': SalesData.objects.order_by('-transaction_date')[:5]
    }
    return render(request, 'core/dashboard.html', context)