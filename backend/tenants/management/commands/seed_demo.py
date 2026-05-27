from django.core.management.base import BaseCommand

from ingestion.models import DataSource, SourceCategory
from records.models import UnitConversionMap
from tenants.models import Tenant


class Command(BaseCommand):
    help = "Seed demo tenant, data sources, and unit conversions."

    def handle(self, *args, **options):
        tenant, _ = Tenant.objects.get_or_create(
            slug="acme-corp",
            defaults={"name": "ACME Corporation"},
        )
        self.stdout.write(f"Tenant: {tenant.slug}")

        for cat, name in [
            (SourceCategory.SAP, "SAP MM Fuel & Procurement"),
            (SourceCategory.UTILITY, "Regional Utility Portal"),
            (SourceCategory.TRAVEL, "Concur Travel Export"),
        ]:
            DataSource.objects.get_or_create(
                tenant=tenant,
                category=cat,
                defaults={"name": name, "is_active": True},
            )

        conversions = [
            ("L", "liters", 1.0),
            ("GAL", "liters", 3.78541),
            ("GAL_US", "liters", 3.78541),
            ("kWh", "kWh", 1.0),
            ("MWh", "kWh", 1000.0),
            ("MWH", "kWh", 1000.0),
            ("mile", "km", 1.60934),
            ("mi", "km", 1.60934),
        ]
        for src, canonical, factor in conversions:
            UnitConversionMap.objects.get_or_create(
                source_unit=src,
                canonical_unit=canonical,
                defaults={"factor_to_canonical": factor},
            )

        self.stdout.write(self.style.SUCCESS("Demo seed complete."))
