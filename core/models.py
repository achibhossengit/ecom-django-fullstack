from django.db import models

class Country(models.Model):
    name_en = models.CharField(max_length=100)
    name_bn = models.CharField(max_length=100)

    def __str__(self):
        return self.name_en


class City(models.Model):
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name="cities")
    name_en = models.CharField(max_length=100)
    name_bn = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name_bn}, {self.country.name_en}"


class Area(models.Model):
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name="areas")
    name_en = models.CharField(max_length=100)
    name_bn = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name_en}, {self.city.name_en}"


class Zone(models.Model):
    area = models.ForeignKey(Area, on_delete=models.CASCADE, related_name="zones")
    name_en = models.CharField(max_length=100)
    name_bn = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.name_en}"