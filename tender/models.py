from django.db import models


# Create your models here.
class TenderFile(models.Model):
    hash = models.CharField(max_length=200)
    offer = models.FileField()

    def __str__(self):
        return self.hash


class OpenTendering(models.Model):
    contract_address = models.CharField(max_length=200)
    name = models.CharField(max_length=200)
    description = models.TextField()
    date_opened = models.DateTimeField(auto_now_add=True, blank=True)
    due_date = models.DateTimeField()

    def __str__(self):
        return self.name
