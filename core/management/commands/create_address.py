from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.conf import settings
import os


class Command(BaseCommand):
    help = "Load address hierarchy fixtures (country, city, area, zone)"

    BASE_FIXTURE_PATH = os.path.join(settings.BASE_DIR, "fixtures")

    FIXTURES = [
        "countries.json",
        "cities.json",
        "areas.json",
        "zones.json",
    ]

    def handle(self, *args, **kwargs):
        for fixture in self.FIXTURES:
            path = os.path.join(self.BASE_FIXTURE_PATH, fixture)

            self.stdout.write(
                self.style.WARNING(
                    f"Loading fixture -> {fixture}"
                )
            )

            if not os.path.exists(path):
                self.stdout.write(
                    self.style.ERROR(
                        f"File not found -> {path}"
                    )
                )
                continue

            try:
                call_command("loaddata", path)
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Loaded -> {fixture}"
                    )
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f"Failed -> {fixture}: {str(e)}"
                    )
                )

        self.stdout.write(
            self.style.SUCCESS(
                "Address fixtures loading completed"
            )
        )