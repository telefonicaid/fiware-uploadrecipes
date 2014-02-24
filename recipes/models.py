from django.db import models

# Create your models here.


class Data(models.Model):
    key = models.CharField(max_length=50)
    value = models.CharField(max_length=50)

    def __str__(self):
        return str(self.value)


class Recipe(models.Model):
    name = models.CharField(max_length=50)
    version = models.CharField(max_length=10)
    description = models.CharField(max_length=200)
    metadata = models.CharField(max_length=200)
    attributes = models.CharField(max_length=200)
