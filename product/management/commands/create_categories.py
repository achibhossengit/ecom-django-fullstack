from django.core.management.base import BaseCommand
from faker import Faker
import random

from product.models import Category


class Command(BaseCommand):
    help = "Create fake categories using Faker"

    def __init__(self):
        super().__init__()
        self.fake = Faker()

    def handle(self, *args, **kwargs):
        category_names = [
            "Fresh Fruits",
            "Vegetables",
            "Dairy Products",
            "Beverages",
            "Snacks",
            "Bakery Items",
            "Frozen Foods",
            "Meat & Fish",
            "Personal Care",
            "Household Essentials",
            "Electronics",
            "Stationery",
            "Baby Products",
            "Organic Foods",
            "Instant Foods",
        ]

        for name in category_names:
            category, created = Category.objects.get_or_create(
                name=name,
                defaults={
                    "description": self.fake.text(max_nb_chars=120)
                }
            )

            if created:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Category created -> {name}"
                    )
                )

        self.stdout.write(
            self.style.SUCCESS(
                "Category seeding completed"
            )
        )