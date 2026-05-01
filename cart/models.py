from django.db import models
from django.db.models import Q
from product.models import Product

class Cart(models.Model):
    user_id = models.IntegerField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart {self.id}"


class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name="items"
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        related_name="cart_items",
        null=True
    )
    quantity = models.PositiveIntegerField(default=1)
    selected = models.BooleanField(default=True)
    added_at = models.DateTimeField(auto_now_add=True)
    
    @property
    def total_price(self):
        return self.product.inventory.price * self.quantity

    def __str__(self):
        return f"{self.quantity} × {self.product.name}"
