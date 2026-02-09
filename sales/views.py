import os
import pandas as pd
from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import SalesData
import uuid

@login_required
def upload_view(request):
    if request.method == 'POST' and request.FILES.get('csv_file'):
        csv_file = request.FILES['csv_file']
        
        # Save file
        user_folder = os.path.join(settings.MEDIA_ROOT, 'uploads', str(request.user.id))
        os.makedirs(user_folder, exist_ok=True)
        file_path = os.path.join(user_folder, csv_file.name)
        
        with open(file_path, 'wb+') as destination:
            for chunk in csv_file.chunks():
                destination.write(chunk)
                
        # Store in session
        request.session['uploaded_file_path'] = file_path
        return redirect('sales_map_columns')
        
    return render(request, 'sales/upload.html')

@login_required
def map_columns_view(request):
    file_path = request.session.get('uploaded_file_path')
    if not file_path or not os.path.exists(file_path):
        messages.error(request, "No file uploaded.")
        return redirect('sales_upload')
    
    try:
        df = pd.read_csv(file_path, nrows=5) # Read only headers and few rows
        headers = df.columns.tolist()
    except Exception as e:
        messages.error(request, f"Error reading CSV: {e}")
        return redirect('sales_upload')

    system_fields = ['transaction_date', 'order_id', 'item_category', 'total_price', 'location_id', 'quantity_sold']

    if request.method == 'POST':
        mapping = {}
        for field in system_fields:
            mapping[field] = request.POST.get(f'map_{field}')
        
        # Process full file
        try:
            full_df = pd.read_csv(file_path)
            # Rename columns
            rename_map = {v: k for k, v in mapping.items() if v}
            full_df.rename(columns=rename_map, inplace=True)
            
            # Filter only mapped columns that exist in DF
            valid_cols = [c for c in system_fields if c in full_df.columns]
            full_df = full_df[valid_cols]
            
            # Bulk create
            sales_objects = []
            for _, row in full_df.iterrows():
                sales_objects.append(SalesData(
                    transaction_date=pd.to_datetime(row.get('transaction_date')),
                    order_id=row.get('order_id', str(uuid.uuid4())[:8]),
                    item_category=row.get('item_category', 'Unknown'),
                    total_price=row.get('total_price', 0.0),
                    location_id=row.get('location_id', 'Default'),
                    quantity_sold=row.get('quantity_sold', 0)
                ))
                
            SalesData.objects.bulk_create(sales_objects)
            messages.success(request, f"Successfully imported {len(sales_objects)} records.")
            return redirect('dashboard')
            
        except Exception as e:
            messages.error(request, f"Import failed: {e}")
            
    return render(request, 'sales/map_columns.html', {'headers': headers, 'system_fields': system_fields})