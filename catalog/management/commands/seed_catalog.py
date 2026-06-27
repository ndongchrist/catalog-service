"""Seed a few demo products (idempotent)."""
from __future__ import annotations

from decimal import Decimal
from typing import Any

from django.core.management.base import BaseCommand

from catalog.models import Product

PRODUCTS = [
    {"sku": "BOOK-001", "name": "The Pragmatic Programmer", "price": Decimal("39.99"), "stock": 50},
    {"sku": "MUG-001", "name": "Kubernetes Coffee Mug", "price": Decimal("12.50"), "stock": 200},
    {"sku": "TEE-001", "name": "Kafka Streams T-Shirt", "price": Decimal("24.00"), "stock": 100},
]


class Command(BaseCommand):
    help = "Seed demo products."

    def handle(self, *args: Any, **opts: Any) -> None:
        for p in PRODUCTS:
            obj, created = Product.objects.update_or_create(sku=p["sku"], defaults=p)
            self.stdout.write(("created " if created else "updated ") + obj.sku)
