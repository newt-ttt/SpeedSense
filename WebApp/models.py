from django.db import models

# Create your models here.

class VehicleInstance(models.Model):
    def __str__(self):
        return str(self.id)
    date = models.CharField(max_length=32)
    speed = models.DecimalField(default=0, decimal_places=0, max_digits=3)
    direction = models.IntegerField(default=0)
    custom_text = models.CharField(max_length=200)