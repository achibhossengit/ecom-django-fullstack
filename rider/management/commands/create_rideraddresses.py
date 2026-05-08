from django.core.management.base import BaseCommand
from faker import Faker
import random

from rider.models import RiderProfile, RiderAddress
from core.models import Zone


class Command(BaseCommand):
    help = "Create rider addresses for all rider profiles"

    def __init__(self):
        super().__init__()
        self.fake = Faker()

    def handle(self, *args, **kwargs):
        rider_profiles = RiderProfile.objects.all()

        zones = list(
            Zone.objects.select_related(
                "area__city__country"
            )
        )

        for rider_profile in rider_profiles:
            active_address_exists = RiderAddress.objects.filter(
                rider=rider_profile,
                is_active=True
            ).exists()

            if active_address_exists:
                continue

            zone = random.choice(zones)

            RiderAddress.objects.create(
                rider=rider_profile,
                country_id=zone.area.city.country_id,
                city_id=zone.area.city_id,
                area_id=zone.area_id,
                zone_id=zone.id,
                is_active=True,
            )

            self.stdout.write(
                self.style.SUCCESS(
                    f"RiderAddress created for {rider_profile.user.username}"
                )
            )

        self.stdout.write(
            self.style.SUCCESS(
                "Rider address seeding completed"
            )
        )