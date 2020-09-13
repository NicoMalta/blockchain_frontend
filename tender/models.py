from django.db import models


# Create your models here.
class TenderFile(models.Model):
    hash = models.CharField(max_length=200)
    offer = models.FileField()

    def __str__(self):
        return self.hash
