from django.db.models.signals import post_delete
from django.dispatch import receiver
from .models import CategoryImage, ProductImage


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
