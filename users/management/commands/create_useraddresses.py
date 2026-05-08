import random
from faker import Faker
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from users.models import UserAddress
from core.models import Zone

User = get_user_model()


class Command(BaseCommand):
    help = "Create user addresses for all users"

    def __init__(self):
        super().__init__()
        self.fake = Faker()

    def handle(self, *args, **kwargs):
        users = User.objects.all()

        zones = list(
            Zone.objects.select_related(
                "area__city__country"
            )
        )

        for user in users:
            active_address_exists = UserAddress.objects.filter(
                user=user,
                is_active=True
            ).exists()

            if active_address_exists:
                continue

            zone = random.choice(zones)

            UserAddress.objects.create(
                user=user,
                name=self.fake.name(),
                country_id=zone.area.city.country_id,
                city_id=zone.area.city_id,
                area_id=zone.area_id,
                zone_id=zone.id,
                phone_number=f"01{random.randint(300000000, 999999999)}",
                description=self.fake.address(),
                type=random.choice([
                    "home",
                    "office",
                    "other"
                ]),
                is_active=True,
            )

            self.stdout.write(
                self.style.SUCCESS(
                    f"Address created for {user.username}"
                )
            )

        self.stdout.write(
            self.style.SUCCESS(
                "User address seeding completed"
            )
        )