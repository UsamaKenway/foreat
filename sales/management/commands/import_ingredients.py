import json
from django.core.management.base import BaseCommand
from sales.models import Ingredient, BillOfMaterial
from django.conf import settings
import os

class Command(BaseCommand):
    help = 'Import ingredients and BOM from JSON'

    def handle(self, *args, **options):
        file_path = os.path.join(settings.BASE_DIR, 'data', 'ingredients_sample.json')
        
        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f'File not found: {file_path}'))
            return

        with open(file_path, 'r') as f:
            data = json.load(f)

        # Import Ingredients
        for ing_data in data.get('ingredients', []):
            ing, created = Ingredient.objects.get_or_create(
                name=ing_data['name'],
                defaults={'unit': ing_data['unit']}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created Ingredient: {ing.name}'))
            else:
                self.stdout.write(f'Ingredient {ing.name} exists')

        # Import BOM
        for bom_data in data.get('bom', []):
            item_cat = bom_data['item_category']
            for ing_entry in bom_data.get('ingredients', []):
                try:
                    ingredient = Ingredient.objects.get(name=ing_entry['name'])
                    bom, created = BillOfMaterial.objects.get_or_create(
                        item_category=item_cat,
                        ingredient=ingredient,
                        defaults={'quantity_per_unit': ing_entry['qty']}
                    )
                    if created:
                        self.stdout.write(self.style.SUCCESS(f'Added BOM: {item_cat} -> {ingredient.name}'))
                except Ingredient.DoesNotExist:
                     self.stdout.write(self.style.WARNING(f'Ingredient {ing_entry["name"]} not found for BOM'))
