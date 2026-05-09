from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from decimal import Decimal
import random

from order.models import (
    Order,
    OrderItem,
    OrderAddress,
    OrderEvent,
    Payment,
    OrderStatus,
)

from users.models import UserAddress
from product.models import Product
from rider.models import RiderAddress

User = get_user_model()


class Command(BaseCommand):
    help = "Create fake orders"

    DELIVERY_CHARGE = Decimal("60")

    def handle(self, *args, **kwargs):
        customers = self.get_customers()
        products = self.get_products()

        if not products:
            self.stdout.write(
                self.style.ERROR(
                    "No products found"
                )
            )
            return

        for customer in customers:
            self.create_orders_for_customer(
                customer=customer,
                products=products,
            )

        self.stdout.write(
            self.style.SUCCESS(
                "Order seeding completed"
            )
        )

    def get_customers(self):
        return User.objects.filter(
            groups__name="customer"
        ).distinct()

    def get_products(self):
        return list(
            Product.objects.select_related("inventory")
        )

    def create_orders_for_customer(self, customer, products):
        user_addresses = UserAddress.objects.filter(
            user=customer
        )

        if not user_addresses.exists():
            self.stdout.write(
                self.style.WARNING(
                    f"No address found for {customer.username}"
                )
            )
            return

        total_orders = random.randint(1, 3)

        for _ in range(total_orders):
            self.create_order(
                customer=customer,
                user_address=random.choice(user_addresses),
                products=products,
            )

    def create_order(self, customer, user_address, products):
        item_payloads, subtotal = self.prepare_order_items(
            products=products
        )

        total = subtotal + self.DELIVERY_CHARGE

        payment_status = self.generate_payment_status()

        order = Order.objects.create(
            customer_id=customer.id,
            customer_name=customer.get_full_name() or customer.username,
            customer_email=customer.email,
            subtotal=subtotal,
            delivery_charge=self.DELIVERY_CHARGE,
            total=total,
            payment_status=payment_status,
            current_status=OrderStatus.PROCESSSING,
        )

        self.create_order_items(
            order=order,
            item_payloads=item_payloads,
        )

        order_address = self.create_order_address(
            order=order,
            user_address=user_address,
        )

        self.create_processing_event(order)

        if payment_status == Order.PaymentStatus.PAID:
            self.create_payment(order)

            self.try_assign_rider(
                order=order,
                city_id=order_address.city_id,
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"Order created -> #{order.id}"
            )
        )

    def prepare_order_items(self, products):
        selected_products = random.sample(
            products,
            k=random.randint(1, 5)
        )

        subtotal = Decimal("0")
        item_payloads = []

        for product in selected_products:

            if not hasattr(product, "inventory"):
                continue

            quantity = random.randint(1, 3)

            subtotal += (
                product.inventory.price * quantity
            )

            item_payloads.append({
                "product": product,
                "quantity": quantity,
                "price": product.inventory.price,
            })

        return item_payloads, subtotal

    def create_order_items(self, order, item_payloads):
        for item in item_payloads:
            OrderItem.objects.create(
                order=order,
                product_id=item["product"].id,
                product_name=item["product"].name,
                sku=item["product"].sku,
                price=item["price"],
                quantity=item["quantity"],
            )

    def create_order_address(self, order, user_address):
        return OrderAddress.objects.create(
            order=order,
            country_id=user_address.country_id,
            city_id=user_address.city_id,
            area_id=user_address.area_id,
            zone_id=user_address.zone_id,
            name=user_address.name,
            phone_number=user_address.phone_number,
            description=user_address.description,
            type=user_address.type,
        )

    def create_processing_event(self, order):
        OrderEvent.objects.create(
            order=order,
            status=OrderStatus.PROCESSSING,
        )

    def create_payment(self, order):
        Payment.objects.create(
            order=order,
            payment_method=Payment.Method.COD,
            amount=order.total,
            payment_status=Payment.PaymentStatus.COMPLETED,
        )

    def try_assign_rider(self, order, city_id):
        should_assign_rider = random.choice([
            True,
            False,
        ])

        if not should_assign_rider:
            return

        rider_address = self.find_matching_rider(
            city_id=city_id
        )

        if not rider_address:
            return

        manager_id = self.get_random_manager_id()

        order.rider_id = rider_address.rider.id
        order.rider_assigned_by = manager_id
        order.current_status = OrderStatus.ASSIGNED_RIDER

        order.save()

        OrderEvent.objects.create(
            order=order,
            status=OrderStatus.ASSIGNED_RIDER,
        )

    def find_matching_rider(self, city_id):
        rider_addresses = RiderAddress.objects.select_related(
            "rider"
        ).filter(
            city_id=city_id,
            is_active=True,
        )

        if not rider_addresses.exists():
            return None

        return random.choice(
            list(rider_addresses)
        )

    def generate_payment_status(self):
        return random.choice([
            Order.PaymentStatus.UNPAID,
            Order.PaymentStatus.PAID,
        ])

    def get_random_manager_id(self):
        managers = list(
            User.objects.filter(
                groups__name="manager"
            ).values_list(
                "id",
                flat=True
            )
        )

        if not managers:
            return None

        return random.choice(managers)