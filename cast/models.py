from django.db import models


class Forecast(models.Model):
    city = models.CharField(max_length=100)
    date = models.DateField()
    min_temperature = models.FloatField()
    max_temperature = models.FloatField()
