from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    help = "Run all seed commands sequentially"

    def add_arguments(self, parser):
        parser.add_argument(
            "--ignore-error",
            action="store_true",
            help="Continue execution even if a command fails",
        )

    def handle(self, *args, **kwargs):
        ignore_error = kwargs["ignore_error"]

        commands = [
            "create_address",
            "load_users",
            "load_rider",
            "load_product",
            "load_cart",
            
            # execute it most last, because it has some dependency over app
            "assign_grouppermissions",
        ]

        for command in commands:
            self.stdout.write(
                self.style.WARNING(
                    f"Running command -> {command}"
                )
            )

            try:
                call_command(command)

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f"[ERROR] {command} failed -> {str(e)}"
                    )
                )

                if not ignore_error:
                    self.stdout.write(
                        self.style.ERROR(
                            "Stopping execution بسبب error (ignore_error=False)"
                        )
                    )
                    break

                self.stdout.write(
                    self.style.WARNING(
                        "Continuing next command due to ignore_error=True"
                    )
                )
                continue

        self.stdout.write(
            self.style.SUCCESS(
                "All commands execution finished"
            )
        )