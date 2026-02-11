from django.contrib import admin
from .models import SalesData, Ingredient, BillOfMaterial

@admin.register(SalesData)
class SalesDataAdmin(admin.ModelAdmin):
    list_display = ('transaction_date', 'item_category', 'quantity_sold', 'total_price', 'location_id')
    list_filter = ('item_category', 'location_id', 'transaction_date')
    search_fields = ('order_id', 'item_category')

@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'unit')
    search_fields = ('name',)

@admin.register(BillOfMaterial)
class BillOfMaterialAdmin(admin.ModelAdmin):
    list_display = ('item_category', 'ingredient', 'quantity_per_unit')
    list_filter = ('item_category', 'ingredient')
    search_fields = ('item_category', 'ingredient__name')