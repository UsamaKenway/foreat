from django.contrib import admin
from .models import TrainingRun, SalesPrediction

@admin.register(TrainingRun)
class TrainingRunAdmin(admin.ModelAdmin):
    list_display = ('id', 'training_date', 'metric_mae', 'metric_mape')
    list_filter = ('training_date',)
    readonly_fields = ('training_date',)

@admin.register(SalesPrediction)
class SalesPredictionAdmin(admin.ModelAdmin):
    list_display = ('item_category', 'target_date', 'predicted_qty', 'training_run')
    list_filter = ('item_category', 'target_date', 'training_run')
    search_fields = ('item_category',)