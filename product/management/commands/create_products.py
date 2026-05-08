from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from faker import Faker
import random
import uuid

from product.models import Product, Category

User = get_user_model()


class Command(BaseCommand):
    help = "Create realistic products with Faker"

    def __init__(self):
        super().__init__()
        self.fake = Faker()

    def handle(self, *args, **kwargs):
        categories = list(Category.objects.all())

        managers = list(
            User.objects.filter(
                groups__name="manager"
            ).values_list("id", flat=True)
        )

        if not categories or not managers:
            self.stdout.write(
                self.style.ERROR("Missing categories or managers")
            )
            return

        created = 0

        for _ in range(20):
            category = random.choice(categories)
            manager_id = random.choice(managers)

            name = self.generate_product_name(category.name)

            if Product.objects.filter(name=name).exists():
                continue

            Product.objects.create(
                name=name,
                sku=f"SKU-{uuid.uuid4().hex[:10].upper()}",
                description=self.fake.text(max_nb_chars=180),
                category=category,
                created_by=manager_id,
            )

            created += 1

            self.stdout.write(
                self.style.SUCCESS(f"Created -> {name}")
            )

        self.stdout.write(
            self.style.SUCCESS(f"Product seeding completed ({created})")
        )

    def generate_product_name(self, category_name):
        prefixes = [
            "Fresh", "Premium", "Organic", "Daily", "Classic",
            "Pure", "Natural", "Special", "Deluxe", "Eco"
        ]

        suffixes = [
            "Pack", "Box", "Bundle", "Item", "Set",
            "Edition", "Choice", "Value Pack", "Collection", "Mix"
        ]

        base = self.fake.word().capitalize()

        return f"{random.choice(prefixes)} {base} {category_name.split()[0]} {random.choice(suffixes)}"