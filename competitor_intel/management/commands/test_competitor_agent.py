from django.core.management.base import BaseCommand
from competitor_intel.services import CompetitorAgent
import json

class Command(BaseCommand):
    help = 'Test the CompetitorAgent with real MCP tools'

    def add_arguments(self, parser):
        parser.add_argument('location', type=str, help='Location to analyze')

    def handle(self, *args, **options):
        location = options['location']
        self.stdout.write(f"Analyzing location: {location}...")
        
        agent = CompetitorAgent()
        results = agent.analyze_location(location)
        
        for comp in results:
            self.stdout.write(self.style.SUCCESS(f"Found: {comp.name} ({comp.cuisine_type})"))
            deals = comp.deals.all()
            if deals:
                for deal in deals:
                    self.stdout.write(f"  - Deal: {deal.deal_title}")
            else:
                self.stdout.write("  - No deals found.")
