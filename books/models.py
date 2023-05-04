from django.db import models


class Book(models.Model):
    class CoverChoices(models.TextChoices):
        HARD = "Hard"
        SOFT = "Soft"

    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    cover = models.CharField(max_length=50, choises=CoverChoices.choices)
    amount = models.IntegerField()
    daily_fee = models.DecimalField(max_digits=5, decimal_places=2)

    @property
    def inventory(self):
        return self.amount
