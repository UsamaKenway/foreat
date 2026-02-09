from django.db import models

class SalesData(models.Model):
    transaction_date = models.DateTimeField()
    order_id = models.CharField(max_length=100)
    item_category = models.CharField(max_length=100)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    location_id = models.CharField(max_length=100)
    quantity_sold = models.IntegerField()

    def __str__(self):
        return f"{self.item_category} - {self.transaction_date}"

class Ingredient(models.Model):
    name = models.CharField(max_length=100)
    unit = models.CharField(max_length=20)

    def __str__(self):
        return self.name

class BillOfMaterial(models.Model):
    item_category = models.CharField(max_length=100, help_text="Matches item_category in SalesData")
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    quantity_per_unit = models.FloatField()

    def __str__(self):
        return f"{self.item_category} uses {self.ingredient.name}"