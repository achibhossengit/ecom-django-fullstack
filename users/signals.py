from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model

User = get_user_model()


@receiver(post_save, sender=User)
def assign_customer_group(sender, instance, created, **kwargs):
    if not created:
        return

    try:
        customer_group = Group.objects.get(name="customer")

        # avoid overriding existing group assignment
        if not instance.groups.exists():
            instance.groups.add(customer_group)

    except Group.DoesNotExist:
        print("Customer group does not exist")