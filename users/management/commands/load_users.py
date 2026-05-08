from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    help = "Load all Users related seed data"

    def handle(self, *args, **kwargs):
        commands = [
            "create_groups",
            "create_userswithgroup",
            "create_useraddresses",
        ]

        for command in commands:
            self.stdout.write(
                self.style.WARNING(
                    f"Running command -> {command}"
                )
            )

            call_command(command)

        self.stdout.write(
            self.style.SUCCESS(
                "All users commands executed successfully"
            )
        )