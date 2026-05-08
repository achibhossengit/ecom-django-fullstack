from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from faker import Faker
import random

from rider.models import RiderApplication
from core.models import Zone

User = get_user_model()


VEHICLE_TYPES = [
    "bike",
    "car",
    "van",
]


class Command(BaseCommand):
    help = "Create rider applications"

    def __init__(self):
        super().__init__()
        self.fake = Faker()

    def handle(self, *args, **kwargs):
        zones = list(
            Zone.objects.select_related(
                "area__city__country"
            )
        )

        self.create_rider_user_applications(zones)
        self.create_customer_user_applications(zones)

        self.stdout.write(
            self.style.SUCCESS(
                "Rider application seeding completed"
            )
        )

    def create_rider_user_applications(self, zones):
        rider_users = User.objects.filter(
            groups__name="rider",
            is_staff=False,
            is_superuser=False,
        ).distinct()

        for user in rider_users:
            if RiderApplication.objects.filter(user=user).exists():
                continue

            zone = random.choice(zones)

            RiderApplication.objects.create(
                user=user,
                full_name=f"{user.first_name} {user.last_name}",
                nid_number=str(
                    random.randint(1000000000, 9999999999)
                ),
                phone_number=f"01{random.randint(300000000, 999999999)}",
                vehicle_type=random.choices(
                    VEHICLE_TYPES,
                    weights=[70, 20, 10],
                    k=1
                )[0],
                license_number=f"LIC-{random.randint(100000, 999999)}",
                country_id=zone.area.city.country_id,
                city_id=zone.area.city_id,
                area_id=zone.area_id,
                zone_id=zone.id,
                status="approved",
            )

            self.stdout.write(
                self.style.SUCCESS(
                    f"Approved application created for {user.username}"
                )
            )

    def create_customer_user_applications(self, zones):
        customer_users = User.objects.filter(
            groups__name="customer",
            is_staff=False,
            is_superuser=False,
        ).distinct()

        for user in customer_users:
            should_create = random.choice([True, False])

            if not should_create:
                continue

            if RiderApplication.objects.filter(user=user).exists():
                continue

            zone = random.choice(zones)

            RiderApplication.objects.create(
                user=user,
                full_name=f"{user.first_name} {user.last_name}",
                nid_number=str(
                    random.randint(1000000000, 9999999999)
                ),
                phone_number=f"01{random.randint(300000000, 999999999)}",
                vehicle_type=random.choices(
                    VEHICLE_TYPES,
                    weights=[70, 20, 10],
                    k=1
                )[0],
                license_number=f"LIC-{random.randint(100000, 999999)}",
                country_id=zone.area.city.country_id,
                city_id=zone.area.city_id,
                area_id=zone.area_id,
                zone_id=zone.id,
                status=random.choice([
                    "pending",
                    "rejected",
                ]),
            )

            self.stdout.write(
                self.style.SUCCESS(
                    f"Customer application created for {user.username}"
                )
            )