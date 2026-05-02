from django.db import models
from django.contrib.auth import get_user_model
from core.models import Country, City, Area, Zone

AuthUser = get_user_model()

class UserAddress(models.Model):
    user = models.ForeignKey(AuthUser, on_delete=models.CASCADE, related_name="addresses")
    name = models.CharField(max_length=200)
    country_id = models.IntegerField()
    city_id = models.IntegerField()
    area_id = models.IntegerField()
    zone_id = models.IntegerField(blank=True, null=True)
    phone_number = models.CharField(max_length=20)
    description = models.TextField(blank=True, null=True)
    type = models.CharField(max_length=50, choices=[("home", "Home"), ("office", "Office"), ("other", "Other")])
    is_active = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user"],
                condition=models.Q(is_active=True),
                name="unique_active_address_per_user"
            )
        ]
        
    def get_full_address(self):
        parts = []
        try:
            if self.zone_id:
                zone = Zone.objects.select_related("area__city__country").get(pk=self.zone_id)
                parts.append(zone.name_en)
                parts.append(zone.area.name_en)
                parts.append(zone.area.city.name_en)
                parts.append(zone.area.city.country.name_en)
            elif self.area_id:
                area = Area.objects.select_related("city__country").get(pk=self.area_id)
                parts.append(area.name_en)
                parts.append(area.city.name_en)
                parts.append(area.city.country.name_en)
            elif self.city_id:
                city = City.objects.select_related("country").get(pk=self.city_id)
                parts.append(city.name_en)
                parts.append(city.country.name_en)
            elif self.country_id:
                country = Country.objects.get(pk=self.country_id)
                parts.append(country.name_en)
        except Exception:
            pass

        return ", ".join(parts)


    def __str__(self):
        return f"Name:{self.name} Country id: {self.country_id}"
