from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from faker import Faker
import random

from cart.models import Cart, CartItem
from product.models import Product

User = get_user_model()


class Command(BaseCommand):
    help = "Create carts with random items for customers"

    def __init__(self):
        super().__init__()
        self.fake = Faker()

    def handle(self, *args, **kwargs):
        customers = User.objects.filter(
            groups__name="customer"
        ).distinct()

        products = list(Product.objects.all())

        if not products:
            self.stdout.write(
                self.style.ERROR("No products found")
            )
            return

        for user in customers:
            # randomly decide whether to create cart or not
            if random.choice([True, False, False]):  # ~33% chance
                if Cart.objects.filter(user_id=user.id).exists():
                    continue

                cart = Cart.objects.create(
                    user_id=user.id
                )

                self.create_cart_items(cart, products)

                self.stdout.write(
                    self.style.SUCCESS(
                        f"Cart created for {user.username}"
                    )
                )

        self.stdout.write(
            self.style.SUCCESS("Cart seeding completed")
        )

    def create_cart_items(self, cart, products):
        selected_products = random.sample(
            products,
            k=random.randint(3, 5)
        )

        for product in selected_products:
            CartItem.objects.create(
                cart=cart,
                product=product,
                quantity=random.randint(1, 3),
                selected=True,
            )