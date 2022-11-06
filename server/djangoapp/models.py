from django.db import models
from django.utils.timezone import now


# Create your models here.

class CarMake(models.Model):
    name = models.CharField(null=False, max_length=35)
    description = models.CharField(null=True, max_length=300)

    def __str__(self):
        return self.name


class CarModel(models.Model):
    car_make = models.ForeignKey(CarMake, null=True, on_delete=models.CASCADE)
    dealer_id = models.IntegerField(null=True)
    name = models.CharField(null=False, max_length=50)
    
    cars = ["Sedan", "SUV", "WAGON", "Others"]
    CAR_CHOICES = [(x, x) for x in cars]
    model_type = models.CharField(
        null=False, max_length=20, choices=CAR_CHOICES, default=cars[-1])

    year = models.DateField()

    def __str__(self):
        return self.name + ", " + str(self.year) + ", " + self.model_type


# <HINT> Create a plain Python class `CarDealer` to hold dealer data


# <HINT> Create a plain Python class `DealerReview` to hold review data
