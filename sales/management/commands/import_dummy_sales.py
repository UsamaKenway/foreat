import random
from datetime import timedelta
from django.utils import timezone
from django.core.management.base import BaseCommand
from sales.models import SalesData
import uuid

class Command(BaseCommand):
    help = 'Generate dummy sales data'

    def handle(self, *args, **options):
        items = [
            ('Pizza', 12.0),
            ('Burger', 8.0),
            ('Salad', 7.0),
            ('Soda', 2.0)
        ]
        
        locations = ['Loc_A', 'Loc_B', 'Loc_C']
        
        end_date = timezone.now()
        start_date = end_date - timedelta(days=365)
        
        current_date = start_date
        total_created = 0
        
        while current_date <= end_date:
            # 5-15 orders per day
            daily_orders = random.randint(5, 15)
            
            for _ in range(daily_orders):
                item_name, base_price = random.choice(items)
                qty = random.randint(1, 5)
                price = base_price * qty
                
                SalesData.objects.create(
                    transaction_date=current_date,
                    order_id=str(uuid.uuid4())[:8],
                    item_category=item_name,
                    total_price=price,
                    location_id=random.choice(locations),
                    quantity_sold=qty
                )
                total_created += 1
            
            current_date += timedelta(days=1)
            
        self.stdout.write(self.style.SUCCESS(f'Successfully created {total_created} sales records.'))
