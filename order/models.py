from django.db import models
from core.models import Country, City, Area, Zone


class OrderStatus(models.TextChoices):
    PROCESSSING     = "processing",     "Processing"
    ASSIGNED_RIDER   = "assigned_rider",   "Assigned Rider"
    ORDER_PICKED_UP  = "order_picked_up",  "Order Picked Up"
    ON_THE_WAY       = "on_the_way",       "On the Way"
    DELIVERED        = "delivered",        "Delivered"
    CANCELLED        = "cancelled",        "Cancelled"

class Order(models.Model):
    class PaymentStatus(models.TextChoices):
        UNPAID   = "unpaid",   "Unpaid"
        PAID   = "paid",   "Paid"

    customer_id = models.IntegerField()
    customer_name = models.CharField(max_length=200)
    customer_email = models.EmailField()
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    delivery_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    rider_id = models.IntegerField(null=True, blank=True)
    rider_assigned_by = models.IntegerField(null=True, blank=True)
    payment_status = models.CharField(max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.UNPAID)
    current_status = models.CharField(max_length=20, choices=OrderStatus.choices, default=OrderStatus.PROCESSSING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        permissions = [
            ('cancel_order', 'Can Cancel Order'),
        ]

    def __str__(self):
        return f"Order #{self.id} — {self.customer_name} ({self.current_status})"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product_id = models.IntegerField()
    product_name = models.CharField(max_length=255)
    sku = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()

    @property
    def total_price(self):
        return self.price * self.quantity

    def __str__(self):
        return f"{self.quantity} × {self.product_name} (Order #{self.order_id})"


class OrderAddress(models.Model):
    class Type(models.TextChoices):
        HOME = "home", "Home"
        OFFICE = "office", "Office"

    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name="address")
    country_id = models.IntegerField()
    city_id = models.IntegerField()
    area_id = models.IntegerField()
    zone_id = models.IntegerField(null=True, blank=True)
    name = models.CharField(max_length=200)
    phone_number = models.CharField(max_length=20)
    description = models.TextField(blank=True, null=True)
    type = models.CharField(max_length=10, choices=Type.choices)

    def get_full_address(self):
        parts = []
        try:
            if self.zone_id:
                zone = Zone.objects.select_related("area__city__country").get(pk=self.zone_id)
                parts.append(zone.name_en)
                parts.append(zone.area.name_en)
                parts.append(zone.area.city.name_en)
                parts.append(zone.area.city.country.name_en)
            elif self.area_id:
                area = Area.objects.select_related("city__country").get(pk=self.area_id)
                parts.append(area.name_en)
                parts.append(area.city.name_en)
                parts.append(area.city.country.name_en)
            elif self.city_id:
                city = City.objects.select_related("country").get(pk=self.city_id)
                parts.append(city.name_en)
                parts.append(city.country.name_en)
            elif self.country_id:
                country = Country.objects.get(pk=self.country_id)
                parts.append(country.name_en)
        except Exception:
            pass

        return ", ".join(parts)

    def __str__(self):
        return f"Address ({self.type}) for Order #{self.order_id}"


class OrderEvent(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="events")
    status = models.CharField(max_length=20, choices=OrderStatus.choices)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"Order #{self.order_id} → {self.status} @ {self.created_at}"


class Payment(models.Model):
    class Method(models.TextChoices):
        COD        = "cod",        "Cash on Delivery"
        BKASH      = "bkash",      "bKash"
        NAGAD      = "nagad",      "Nagad"
        SSLCOMMERZ = "sslcommerz", "SSLCommerz"

    class PaymentStatus(models.TextChoices):
        PENDING   = "pending",   "Pending"
        COMPLETED = "completed", "Completed"
        FAILED    = "failed",    "Failed"
        REFUNDED  = "refunded",  "Refunded"

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="payments")
    payment_method = models.CharField(max_length=20, choices=Method.choices)
    transaction_id = models.CharField(max_length=100, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.CharField(max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment ({self.payment_method} — {self.payment_status}) for Order #{self.order_id}"