from django.core.management.base import BaseCommand
from reservations.models import ReservationSignal
from datetime import date, timedelta
import random

class Command(BaseCommand):
    help = 'Seed dummy reservation data'

    def handle(self, *args, **kwargs):
        ReservationSignal.objects.all().delete()
        
        platforms = ['OpenTable', 'Internal', 'Resy']
        
        for i in range(30):
            target_date = date.today() - timedelta(days=i)
            booking_count = random.randint(20, 100)
            # Simulate some no-shows (90% to 100% show rate)
            actual_arrivals = int(booking_count * random.uniform(0.7, 1.0))
            
            ReservationSignal.objects.create(
                target_date=target_date,
                booking_count=booking_count,
                party_size_total=booking_count * 2,
                actual_arrivals=actual_arrivals,
                platform=random.choice(platforms)
            )
            
        self.stdout.write(self.style.SUCCESS('Successfully seeded 30 days of reservation data'))
