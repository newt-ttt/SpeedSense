from django.db import models

# Create your models here.

class VehicleInstance(models.Model):
    def __str__(self):
        return str(self.id)
    date = models.DateTimeField(max_length=32)
    speeds = models.CharField(max_length=4096)
    direction = models.IntegerField(default=0)
    custom_text = models.CharField(max_length=200, default="TEST")