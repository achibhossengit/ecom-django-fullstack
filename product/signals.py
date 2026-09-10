from django.core.cache import cache
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from .models import Category, CategoryImage, Inventory, Product, ProductImage


# =========================================
# Remove Orphaned Images from Media Storage
# ========================================
@receiver(post_delete, sender=CategoryImage)
def delete_category_image(sender, instance, **kwargs):
    if instance.image:
        instance.image.delete(save=False)

@receiver(post_delete, sender=ProductImage)
def delete_product_image(sender, instance, **kwargs):
    if instance.image:
        instance.image.delete(save=False)


def invalidate_homepage_catalog(**kwargs):
    cache.delete("homepage_catalog")


# Drop cached homepage catalog when products or categories change.
for _model in (Product, Category, Inventory, ProductImage, CategoryImage):
    post_save.connect(invalidate_homepage_catalog, sender=_model, weak=False)
    post_delete.connect(invalidate_homepage_catalog, sender=_model, weak=False)
