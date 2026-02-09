from django.db import models
import uuid

class TrainingRun(models.Model):
    model_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    training_date = models.DateTimeField(auto_now_add=True)
    metric_mae = models.FloatField()
    metric_mape = models.FloatField()
    model_path = models.CharField(max_length=255)

    def __str__(self):
        return f"Run {self.model_id} - MAE: {self.metric_mae}"

class SalesPrediction(models.Model):
    training_run = models.ForeignKey(TrainingRun, on_delete=models.CASCADE, null=True, blank=True)
    item_category = models.CharField(max_length=100)
    target_date = models.DateTimeField()
    predicted_qty = models.FloatField()
    confidence_upper = models.FloatField(null=True, blank=True)
    confidence_lower = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"{self.item_category} on {self.target_date}: {self.predicted_qty}"