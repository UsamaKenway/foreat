from django.db import models

class WeatherSignal(models.Model):
    timestamp = models.DateTimeField()
    temperature = models.FloatField()
    precipitation = models.FloatField()

    def __str__(self):
        return f"Weather at {self.timestamp}"

class LocalEvent(models.Model):
    date = models.DateField()
    event_name = models.CharField(max_length=200)
    impact_score = models.IntegerField(help_text="1-10 impact score")

    def __str__(self):
        return f"{self.event_name} on {self.date}"