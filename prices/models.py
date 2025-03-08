from django.db import models

class Price(models.Model):
    commodity = models.CharField(max_length=255)
    market = models.CharField(max_length=255)
    district = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    min_price = models.DecimalField(max_digits=10, decimal_places=2)
    max_price = models.DecimalField(max_digits=10, decimal_places=2)
    modal_price = models.DecimalField(max_digits=10, decimal_places=2)
    arrival_date = models.DateField()

    class Meta:
        db_table = 'daily_prices_price' 
        managed = False
        unique_together = ['commodity', 'market', 'district', 'arrival_date']

    def __str__(self):
        return f"{self.commodity} at {self.market} on {self.arrival_date}"