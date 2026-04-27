from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=255)
    sku = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name="products",
    )
    # created_by is intentionally stored as a plain ID (not FK) for scalability
    created_by = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


# class ProductImage(models.Model):
#     product = models.ForeignKey(
#         Product,
#         on_delete=models.CASCADE,
#         related_name="images",
#     )
#     image = models.ImageField(upload_to="products/")
#     is_default = models.BooleanField(default=False)

#     def __str__(self):
#         return f"Image for {self.product.name} (default={self.is_default})"


# class CategoryImage(models.Model):
#     category = models.ForeignKey(
#         Category,
#         on_delete=models.CASCADE,
#         related_name="images",
#     )
#     image = models.ImageField(upload_to="categories/")
#     is_default = models.BooleanField(default=False)

#     def __str__(self):
#         return f"Image for {self.category.name} (default={self.is_default})"


class Inventory(models.Model):
    product = models.OneToOneField(
        Product,
        on_delete=models.CASCADE,
        related_name="inventory",
    )
    quantity = models.PositiveIntegerField(default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    updated_at = models.DateTimeField(auto_now=True)


    class Meta:
        verbose_name_plural = "Inventories"

    def __str__(self):
        return f"Inventory for {self.product.name}"


class QuantityHistory(models.Model):
    class ActionType(models.TextChoices):
        STOCK_IN = "STOCK_IN", "Stock In"          # new stock added from supplier
        SALE = "SALE", "Sale"                       # quantity reduced by a customer order
        RETURN = "RETURN", "Return"                 # customer returned item, stock restored
        ADJUSTMENT = "ADJUSTMENT", "Adjustment"    # manual correction by admin
        DAMAGE = "DAMAGE", "Damage"                # stock written off due to damage/expiry
        TRANSFER = "TRANSFER", "Transfer"          # stock moved between warehouses/locations

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="quantity_histories",
    )
    action_type = models.CharField(max_length=10, choices=ActionType.choices)
    last_quantity = models.PositiveIntegerField()
    quantity_changed = models.IntegerField()  # can be negative (stock removal)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.IntegerField(blank=True, null=True)

    class Meta:
        verbose_name_plural = "Quantity Histories"

    def __str__(self):
        return f"{self.action_type} | Inventory {self.inventory_id} @ {self.created_at}"


class PriceHistory(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="price_histories",
    )
    last_price = models.DecimalField(max_digits=10, decimal_places=2)
    price_changed = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.IntegerField(blank=True, null=True)

    class Meta:
        verbose_name_plural = "Price Histories"

    def __str__(self):
        return f"Price change for Inventory {self.inventory_id} @ {self.created_at}"


class Review(models.Model):
    # user_id and order_id are intentionally plain IDs (not FK) for scalability
    user_id = models.IntegerField()
    order_id = models.IntegerField()
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="reviews",
    )
    rating = models.PositiveSmallIntegerField()  # e.g. 1–5
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Review by user {self.user_id} on {self.product.name} ({self.rating})"