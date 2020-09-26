from django.db import models


# Create your models here.
class Medicine(models.Model):
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=100)
    description = models.CharField(max_length=100)


class Diagnosis(models.Model):
    description = models.CharField(max_length=100)
    createDate = models.CharField(max_length=100)
