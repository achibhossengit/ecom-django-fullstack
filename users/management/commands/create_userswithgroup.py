from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from faker import Faker

User = get_user_model()


class Command(BaseCommand):
    help = "Seed users and related data"

    def __init__(self):
        super().__init__()
        self.fake = Faker()

    def handle(self, *args, **kwargs):
        call_command("create_groups")

        self.create_users()

        self.stdout.write(
            self.style.SUCCESS("Users created successfully")
        )

    def create_users(self):
        self.create_group_users("manager", 5)
        self.create_group_users("customer", 15)
        self.create_group_users("rider", 30)

    def create_group_users(self, group_name, total):
        group = Group.objects.get(name=group_name)

        for i in range(total):
            first_name = self.fake.first_name()
            last_name = self.fake.last_name()

            username = f"{group_name}_{first_name.lower()}_{i}"
            email = f"{username}@example.com"

            if User.objects.filter(username=username).exists():
                continue

            user = User.objects.create_user(
                username=username,
                email=email,
                password="Test1234!",
                first_name=first_name,
                last_name=last_name,
            )

            user.groups.add(group)

            self.stdout.write(
                self.style.SUCCESS(
                    f"{group_name.upper()} created -> {username}"
                )
            )