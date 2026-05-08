from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group


class Command(BaseCommand):
    help = "Seed users and related data"

    def handle(self, *args, **kwargs):
        self.create_groups()

        self.stdout.write(
            self.style.SUCCESS("Groups created successfully")
        )

    def create_groups(self):
        groups = [
            "customer",
            "rider",
            "manager",
        ]

        for group_name in groups:
            print(group_name)
            Group.objects.get_or_create(name=group_name)