from django.core.management.base import BaseCommand
import os, random
from django.core.files import File
from product.models import Category, CategoryImage

class Command(BaseCommand):
    help = "Assign one random image from a folder to each category"

    def add_arguments(self, parser):
        parser.add_argument("folder", type=str, help="Path to image folder")

    def handle(self, *args, **options):
        folder = options["folder"]
        files = [
            os.path.join(folder, f)
            for f in os.listdir(folder)
            if f.lower().endswith((".jpg", ".png"))
        ]
        if not files:
            self.stdout.write(self.style.ERROR("No image files found in folder"))
            return

        categories = list(Category.objects.all())
        for category in categories:
            path = random.choice(files)  # pick one image
            with open(path, "rb") as f:
                CategoryImage.objects.create(
                    category=category,
                    image=File(f, name=f"{os.path.basename(path)}"),
                )

        self.stdout.write(self.style.SUCCESS("One image assigned per category"))
