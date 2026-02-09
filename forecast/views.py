from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from sales.models import SalesData, BillOfMaterial
from .models import TrainingRun, SalesPrediction
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_absolute_percentage_error
from datetime import timedelta
import json

@login_required
def training_hub(request):
    runs = TrainingRun.objects.order_by('-training_date')[:5]
    
    # Prepare data for charts (Last Run)
    last_run = runs.first()
    predictions = []
    if last_run:
        preds = SalesPrediction.objects.filter(training_run=last_run).order_by('target_date')
        for p in preds:
            predictions.append({
                'date': p.target_date.strftime('%Y-%m-%d'),
                'item': p.item_category,
                'qty': p.predicted_qty
            })
            
    # Ingredient Forecast
    ingredient_needs = []
    if predictions:
        # Group predictions by item
        df_pred = pd.DataFrame(predictions)
        if not df_pred.empty:
            summary = df_pred.groupby('item')['qty'].sum().reset_index()
            
            for _, row in summary.iterrows():
                boms = BillOfMaterial.objects.filter(item_category=row['item'])
                for bom in boms:
                    ingredient_needs.append({
                        'ingredient': bom.ingredient.name,
                        'unit': bom.ingredient.unit,
                        'qty': row['qty'] * bom.quantity_per_unit
                    })
                    
    # Aggregate ingredients
    if ingredient_needs:
        df_ing = pd.DataFrame(ingredient_needs)
        ing_summary = df_ing.groupby(['ingredient', 'unit'])['qty'].sum().reset_index().to_dict('records')
    else:
        ing_summary = []

    context = {
        'runs': runs,
        'predictions_json': json.dumps(predictions),
        'ingredient_needs': ing_summary
    }
    return render(request, 'forecast/training_hub.html', context)

@login_required
def train_model(request):
    if request.method == 'POST':
        # 1. Fetch Data
        sales_qs = SalesData.objects.all().values('transaction_date', 'item_category', 'quantity_sold')
        if not sales_qs:
             return JsonResponse({'status': 'error', 'message': 'No sales data to train on.'})
             
        df = pd.DataFrame(list(sales_qs))
        df['transaction_date'] = pd.to_datetime(df['transaction_date'])
        
        # Aggregate to Daily Sales per Item
        df = df.groupby(['transaction_date', 'item_category'])['quantity_sold'].sum().reset_index()
        
        # 2. Feature Engineering
        df['dow'] = df['transaction_date'].dt.dayofweek
        df['month'] = df['transaction_date'].dt.month
        df['day'] = df['transaction_date'].dt.day
        
        # One-hot encode Item Category
        df = pd.get_dummies(df, columns=['item_category'], prefix='item', drop_first=False) # Keep all for simple reconstruction if needed
        
        # Target
        y = df['quantity_sold']
        X = df.drop(['quantity_sold', 'transaction_date'], axis=1)
        
        # 3. Train
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False) # Time series split roughly
        
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)
        
        # 4. Metrics
        preds_test = model.predict(X_test)
        mae = mean_absolute_error(y_test, preds_test)
        mape = mean_absolute_percentage_error(y_test, preds_test)
        
        # Save Run
        run = TrainingRun.objects.create(
            metric_mae=mae,
            metric_mape=mape,
            model_path="memory_only_for_prototype"
        )
        
        # 5. Forecast Future (Next 14 Days) for each Item Category
        # We need a list of categories.
        # Re-fetch unique categories from DB to be sure
        categories = SalesData.objects.values_list('item_category', flat=True).distinct()
        
        last_date = df['transaction_date'].max()
        future_dates = [last_date + timedelta(days=x) for x in range(1, 15)]
        
        bulk_preds = []
        
        for cat in categories:
            for date in future_dates:
                # Construct feature vector
                # This is a bit simplified. In reality we need exact same columns.
                # We'll create a single row DF and fill missing cols with 0
                
                row = {
                    'dow': date.dayofweek,
                    'month': date.month,
                    'day': date.day,
                }
                # Set item_{cat} = 1, others 0
                for c in categories:
                    col_name = f'item_{c}'
                    if col_name in X.columns:
                        row[col_name] = 1 if c == cat else 0
                        
                # Ensure all X columns are present
                feat_df = pd.DataFrame([row])
                for col in X.columns:
                    if col not in feat_df.columns:
                        feat_df[col] = 0
                
                # Align columns
                feat_df = feat_df[X.columns]
                
                pred_qty = model.predict(feat_df)[0]
                
                bulk_preds.append(SalesPrediction(
                    training_run=run,
                    item_category=cat,
                    target_date=date,
                    predicted_qty=max(0, pred_qty) # No negative sales
                ))
                
        SalesPrediction.objects.bulk_create(bulk_preds)
        
        return JsonResponse({'status': 'success', 'mae': mae, 'mape': mape})
        
    return JsonResponse({'status': 'error', 'message': 'Invalid method'})