import os
from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    help = "Load all order related seed data"

    def handle(self, *args, **kwargs):
        commands = [
            ("create_orders", None),
        ]

        for command_name, arg in commands:
            self.stdout.write(
                self.style.WARNING(
                    f"Running command -> {command_name}"
                )
            )

            if arg:
                if not os.path.exists(arg):
                    self.stdout.write(
                        self.style.WARNING(
                            f"Path not found -> {arg}, skipping {command_name}"
                        )
                    )
                    continue

                call_command(command_name, arg)
            else:
                call_command(command_name)

        self.stdout.write(
            self.style.SUCCESS(
                "All order commands executed successfully"
            )
        )