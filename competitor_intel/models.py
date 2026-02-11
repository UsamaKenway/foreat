from django.db import models

class Competitor(models.Model):
    name = models.CharField(max_length=200)
    google_place_id = models.CharField(max_length=200, unique=True, null=True, blank=True)
    location_name = models.CharField(max_length=200) # City/Area
    address = models.TextField(null=True, blank=True)
    cuisine_type = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.name

class CompetitorTraffic(models.Model):
    competitor = models.ForeignKey(Competitor, on_delete=models.CASCADE, related_name='traffic_logs')
    date = models.DateField()
    estimated_visits = models.IntegerField() # Derived from Google Maps "Popular Times"
    traffic_score = models.IntegerField() # Normalized 0-100

    def __str__(self):
        return f"{self.competitor.name} - {self.date}"

class CompetitorDeal(models.Model):
    competitor = models.ForeignKey(Competitor, on_delete=models.CASCADE, related_name='deals')
    date_observed = models.DateField()
    deal_title = models.CharField(max_length=300)
    deal_source_url = models.URLField(max_length=500, null=True, blank=True)
    impact_on_traffic = models.FloatField(null=True, blank=True) # Calculated correlation

    def __str__(self):
        return f"{self.competitor.name} - {self.deal_title}"
