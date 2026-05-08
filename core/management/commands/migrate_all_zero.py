from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.apps import apps


class Command(BaseCommand):
    help = "Unapply all migrations for all installed apps"

    def handle(self, *args, **kwargs):
        app_configs = apps.get_app_configs()

        for app_config in app_configs:
            app_label = app_config.label

            try:
                self.stdout.write(
                    self.style.WARNING(
                        f"Unapplying migrations -> {app_label}"
                    )
                )

                call_command(
                    "migrate",
                    app_label,
                    "zero",
                    verbosity=0
                )

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f"Failed -> {app_label}: {str(e)}"
                    )
                )

        self.stdout.write(
            self.style.SUCCESS(
                "All app migrations unapplied"
            )
        )