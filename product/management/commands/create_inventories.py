from django.core.management.base import BaseCommand
from faker import Faker
import random
from decimal import Decimal

from product.models import Product, Inventory


class Command(BaseCommand):
    help = "Create inventory for all products"

    def __init__(self):
        super().__init__()
        self.fake = Faker()

    def handle(self, *args, **kwargs):
        products = Product.objects.all()

        if not products.exists():
            self.stdout.write(
                self.style.ERROR("No products found")
            )
            return

        for product in products:
            if hasattr(product, "inventory"):
                continue

            Inventory.objects.create(
                product=product,
                quantity=random.randint(10, 500),
                price=Decimal(
                    round(random.uniform(5, 2000), 2)
                ),
            )

            self.stdout.write(
                self.style.SUCCESS(
                    f"Inventory created -> {product.name}"
                )
            )

        self.stdout.write(
            self.style.SUCCESS(
                "Inventory seeding completed"
            )
        )