from django.db import models
from django.contrib.auth import get_user_model

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
    zone_id = models.IntegerField()
    is_active = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["rider"],
                condition=models.Q(is_active=True),
                name="unique_active_address_per_rider"
            )
        ]

    def save(self, *args, **kwargs):
        if self.is_active:
            RiderAddress.objects.filter(
                rider=self.rider,
                is_active=True
            ).exclude(pk=self.pk).update(is_active=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"RiderAddress({self.rider.user.username}, Active={self.is_active})"