from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from faker import Faker
import random

from rider.models import RiderProfile

User = get_user_model()


VEHICLE_TYPES = [
    "bike",
    "car",
    "van",
]


class Command(BaseCommand):
    help = "Create rider profiles for all rider users"

    def __init__(self):
        super().__init__()
        self.fake = Faker()

    def handle(self, *args, **kwargs):
        rider_users = User.objects.filter(
            groups__name="rider"
        ).distinct()

        for user in rider_users:
            rider_profile_exists = RiderProfile.objects.filter(
                user=user
            ).exists()

            if rider_profile_exists:
                continue

            RiderProfile.objects.create(
                user=user,
                full_name=f"{user.first_name} {user.last_name}",
                nid_number=str(
                    random.randint(1000000000, 9999999999)
                ),
                phone_number=f"01{random.randint(300000000, 999999999)}",
                license_number=f"LIC-{random.randint(100000, 999999)}",
                vehicle_type=random.choices(
                    VEHICLE_TYPES,
                    weights=[70, 20, 10],
                    k=1
                )[0],
                is_active=random.choice([True, False]),
            )

            self.stdout.write(
                self.style.SUCCESS(
                    f"RiderProfile created for {user.username}"
                )
            )

        self.stdout.write(
            self.style.SUCCESS(
                "Rider profile seeding completed"
            )
        )