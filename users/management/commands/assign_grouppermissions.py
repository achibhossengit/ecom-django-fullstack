# assign_group_permissions.py

from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission


class Command(BaseCommand):
    help = "Assign permissions to groups"

    GROUP_PERMISSIONS = {
        "manager": [
            "core.view_managerdashboard",

            "order.change_order",
            "order.view_order",

            "order.view_orderaddress",

            "order.add_orderevent",
            "order.change_orderevent",
            "order.view_orderevent",

            "order.view_orderitem",

            "order.view_payment",

            "product.add_category",
            "product.change_category",
            "product.delete_category",
            "product.view_category",

            "product.add_categoryimage",
            "product.change_categoryimage",
            "product.delete_categoryimage",
            "product.view_categoryimage",

            "product.add_inventory",
            "product.change_inventory",
            "product.delete_inventory",
            "product.view_inventory",

            "product.add_pricehistory",
            "product.view_pricehistory",

            "product.add_product",
            "product.change_product",
            "product.delete_product",
            "product.view_product",

            "product.add_productimage",
            "product.change_productimage",
            "product.delete_productimage",
            "product.view_productimage",

            "product.add_quantityhistory",
            "product.view_quantityhistory",

            "product.view_review",

            "rider.view_rideraddress",

            "rider.change_riderapplication",
            "rider.view_riderapplication",

            "rider.change_riderprofile",
            "rider.view_riderprofile",
        ],

        "customer": [
            "cart.view_cart",

            "cart.add_cartitem",
            "cart.change_cartitem",
            "cart.delete_cartitem",
            "cart.view_cartitem",

            "order.add_order",
            "order.cancel_order",
            "order.view_order",

            "order.view_orderaddress",
            "order.view_orderevent",
            "order.view_orderitem",

            "order.add_payment",
            "order.view_payment",

            "product.view_category",
            "product.view_categoryimage",
            "product.view_inventory",
            "product.view_product",
            "product.view_productimage",
            "product.view_quantityhistory",

            "product.add_review",
            "product.change_review",
            "product.delete_review",
            "product.view_review",

            "rider.view_rideraddress",

            "rider.add_riderapplication",
            "rider.change_riderapplication",
            "rider.delete_riderapplication",
            "rider.view_riderapplication",

            "rider.view_riderprofile",
        ],

        "rider": [
            "core.view_riderdashboard",

            "order.view_order",
            "order.view_orderaddress",

            "order.add_orderevent",

            "order.view_orderitem",

            "rider.add_rideraddress",
            "rider.change_rideraddress",
            "rider.delete_rideraddress",
            "rider.view_rideraddress",

            "rider.view_riderapplication",

            "rider.change_riderprofile",
            "rider.view_riderprofile",
        ]
    }

    def handle(self, *args, **kwargs):
        for group_name, permissions in self.GROUP_PERMISSIONS.items():

            try:
                group = Group.objects.get(name=group_name)

            except Group.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(
                        f"Group not found -> {group_name}"
                    )
                )
                continue

            for permission_path in permissions:
                try:
                    app_label, codename = permission_path.split(".")

                    permission = Permission.objects.get(
                        content_type__app_label=app_label,
                        codename=codename,
                    )

                    group.permissions.add(permission)

                    self.stdout.write(
                        self.style.SUCCESS(
                            f"[OK] {group_name} -> {permission_path}"
                        )
                    )

                except Permission.DoesNotExist:
                    self.stdout.write(
                        self.style.ERROR(
                            f"[NOT FOUND] {group_name} -> {permission_path}"
                        )
                    )

                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(
                            f"[ERROR] {group_name} -> {permission_path} -> {str(e)}"
                        )
                    )

        self.stdout.write(
            self.style.SUCCESS(
                "Permission assignment completed"
            )
        )