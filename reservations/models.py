from django.db import models

class ReservationSignal(models.Model):
    target_date = models.DateField()
    booking_count = models.IntegerField()
    party_size_total = models.IntegerField()
    actual_arrivals = models.IntegerField(default=0)
    platform = models.CharField(max_length=50) # e.g., "OpenTable", "Internal"
    
    @property
    def no_show_rate(self):
        if self.booking_count == 0:
            return 0
        return max(0, self.booking_count - self.actual_arrivals) / self.booking_count * 100

    def __str__(self):
        return f"{self.target_date} - {self.platform} ({self.booking_count} bookings)"

class NoShowTrainingRun(models.Model):
    training_date = models.DateTimeField(auto_now_add=True)
    mae = models.FloatField()
    model_path = models.CharField(max_length=200)

    def __cl__(self):
        return f"Training on {self.training_date}"
