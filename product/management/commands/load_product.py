from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.conf import settings
import os


class Command(BaseCommand):
    help = "Load all product related seed data"

    CATEGORY_IMAGE_PATH = os.path.join(
        settings.BASE_DIR,
        "fixtures",
        "category_images",
    )

    PRODUCT_IMAGE_PATH = os.path.join(
        settings.BASE_DIR,
        "fixtures",
        "product_images",
    )

    def handle(self, *args, **kwargs):
        commands = [
            ("create_categories", None),
            ("create_products", None),
            ("create_inventories", None),
            ("upload_categoryimages", self.CATEGORY_IMAGE_PATH),
            ("upload_productimages", self.PRODUCT_IMAGE_PATH),
        ]

        for command_name, arg in commands:
            self.stdout.write(
                self.style.WARNING(
                    f"Running command -> {command_name}"
                )
            )

            if arg:
                if not os.path.exists(arg):
                    self.stdout.write(
                        self.style.WARNING(
                            f"Path not found -> {arg}, skipping {command_name}"
                        )
                    )
                    continue

                call_command(command_name, arg)
            else:
                call_command(command_name)

        self.stdout.write(
            self.style.SUCCESS(
                "All product commands executed successfully"
            )
        )