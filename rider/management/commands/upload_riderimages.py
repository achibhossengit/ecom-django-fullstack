from django.core.management.base import BaseCommand
import os, random
from django.core.files import File

from rider.models import RiderProfile


class Command(BaseCommand):
    help = "Upload random profile images for rider profiles"

    def add_arguments(self, parser):
        parser.add_argument(
            "folder",
            type=str,
            help="Path to profile image folder"
        )

    def handle(self, *args, **options):
        folder = options["folder"]

        files = [
            os.path.join(folder, f)
            for f in os.listdir(folder)
            if f.lower().endswith((".jpg", ".png", ".jpeg"))
        ]

        if not files:
            self.stdout.write(
                self.style.ERROR("No image files found in folder")
            )
            return

        riders = list(RiderProfile.objects.all())

        if not riders:
            self.stdout.write(
                self.style.ERROR("No rider profiles found")
            )
            return

        for rider in riders:
            try:
                path = random.choice(files)

                with open(path, "rb") as f:
                    rider.profile_image.save(
                        os.path.basename(path),
                        File(f),
                        save=True
                    )

                self.stdout.write(
                    self.style.SUCCESS(
                        f"[OK] Rider -> {rider.user.username} | Image -> {os.path.basename(path)}"
                    )
                )

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f"[FAIL] Rider -> {rider.user.username} | Error -> {str(e)}"
                    )
                )

        self.stdout.write(
            self.style.SUCCESS("Rider profile image upload completed")
        )