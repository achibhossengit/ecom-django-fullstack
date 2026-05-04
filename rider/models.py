from django.db import models
from django.contrib.auth import get_user_model
from core.models import Country, City, Area, Zone

AuthUser = get_user_model()


VEHICLE_TYPE_CHOICES = [
    ("bike", "Bike"),
    ("car", "Car"),
    ("van", "Van"),
]


class RiderProfile(models.Model):
    user = models.OneToOneField(
        AuthUser,
        on_delete=models.CASCADE,
        related_name="rider_profile"
    )
    full_name = models.CharField(max_length=200)
    profile_image = models.ImageField(upload_to='rider_profiles', null=True, blank=True)
    phone_number = models.CharField(max_length=20)
    vehicle_type = models.CharField(
        max_length=20,
        choices=VEHICLE_TYPE_CHOICES
    )
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"RiderProfile({self.user.username})"


class RiderApplication(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    ]

    user = models.ForeignKey(
        AuthUser,
        on_delete=models.CASCADE,
        related_name="rider_applications"
    )
    full_name = models.CharField(max_length=100)
    nid_number = models.CharField(max_length=20)
    vehicle_type = models.CharField(
        max_length=20,
        choices=VEHICLE_TYPE_CHOICES
    )
    license_number = models.CharField(max_length=30)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending"
    )
    applied_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Application({self.user.username}, {self.status})"


class RiderAddress(models.Model):
    rider = models.ForeignKey(
        RiderProfile,
        on_delete=models.CASCADE,
        related_name="addresses"
    )
    country_id = models.IntegerField()
    city_id = models.IntegerField()
    area_id = models.IntegerField()
    zone_id = models.IntegerField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["rider"],
                condition=models.Q(is_active=True),
                name="unique_active_address_per_rider"
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
    

    def save(self, *args, **kwargs):
        if self.is_active:
            RiderAddress.objects.filter(
                rider=self.rider,
                is_active=True
            ).exclude(pk=self.pk).update(is_active=False)
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        was_active = self.is_active
        rider = self.rider
        super().delete(*args, **kwargs)
        if was_active:
            # Try to activate another address
            other = RiderAddress.objects.filter(rider=rider).first()
            if other:
                other.is_active = True
                other.save()

    def __str__(self):
        return f"RiderAddress({self.rider.user.username}, Active={self.is_active})"