import os
from openai import OpenAI
from .models import Competitor, CompetitorTraffic, CompetitorDeal
from datetime import date, timedelta
import random

class CompetitorAgent:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        # Initialize client only if key is available, else we will use mock data
        self.client = OpenAI(api_key=self.api_key) if self.api_key else None

    def analyze_location(self, location_name):
        """
        Main workflow for competitor analysis using simulated MCP tools.
        """
        # 1. Search for competitors (Simulating mcp-google-map)
        competitors_data = self._get_competitors(location_name)
        
        results = []
        for comp_data in competitors_data:
            # Save or update competitor
            competitor, created = Competitor.objects.update_or_create(
                google_place_id=comp_data['place_id'],
                defaults={
                    'name': comp_data['name'],
                    'location_name': location_name,
                    'address': comp_data['address'],
                    'cuisine_type': comp_data['cuisine']
                }
            )
            
            # 2. Get traffic data (Simulating Google Map Popular Times)
            self._fetch_traffic_data(competitor)
            
            # 3. Get deals (Simulating Firecrawl/Browser scraping)
            self._fetch_deals(competitor)
            
            results.append(competitor)
            
        return results

    def _get_competitors(self, location):
        # In a real MCP setup, this would be a tool call to google-maps todo
        # Simulation:
        return [
            {'name': f'Green Bistro {location}', 'place_id': f'place_{location}_1', 'address': f'123 Teal St, {location}', 'cuisine': 'Healthy'},
            {'name': f'Urban Eats {location}', 'place_id': f'place_{location}_2', 'address': f'456 Mint Ave, {location}', 'cuisine': 'Fusion'},
            {'name': f'The Healthy Hub {location}', 'place_id': f'place_{location}_3', 'address': f'789 Sage Rd, {location}', 'cuisine': 'Vegan'}
        ]

    def _fetch_traffic_data(self, competitor):
        # Simulate fetching last 14 days of traffic
        for i in range(14):
            d = date.today() - timedelta(days=i)
            CompetitorTraffic.objects.update_or_create(
                competitor=competitor,
                date=d,
                defaults={
                    'estimated_visits': random.randint(50, 200),
                    'traffic_score': random.randint(30, 95)
                }
            )

    def _fetch_deals(self, competitor):
        # Simulate finding a deal with Firecrawl
        deals = [
            "Happy Hour 50% Off Drinks",
            "Buy One Get One Pizza",
            "Lunch Special: Salad + Soda for $12",
            "No active deals"
        ]
        deal_title = random.choice(deals)
        if deal_title != "No active deals":
            CompetitorDeal.objects.update_or_create(
                competitor=competitor,
                date_observed=date.today(),
                deal_title=deal_title,
                defaults={
                    'deal_source_url': 'https://example.com/deals',
                    'impact_on_traffic': random.uniform(0.05, 0.25)
                }
            )
