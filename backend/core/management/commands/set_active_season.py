from django.core.management.base import BaseCommand
from django.db import transaction

from core.models import Season


class Command(BaseCommand):
    help = "Create Season if missing, then set it as active."

    def add_arguments(self, parser):
        parser.add_argument(
            "--season",
            type=int,
            required=True,
            help="Season version number, e.g. 16",
        )

    def handle(self, *args, **options):
        season_value = options["season"]

        with transaction.atomic():
            season, created = Season.objects.get_or_create(version=season_value)

            Season.objects.exclude(pk=season.pk).update(is_active=False)

            if not season.is_active:
                season.is_active = True
                season.save(update_fields=["is_active"])

        if created:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Created season version={season_value} and set as active."
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f"Set season version={season_value} as active.")
            )
