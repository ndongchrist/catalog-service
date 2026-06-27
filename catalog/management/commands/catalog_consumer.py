"""catalog-consumer — runs as its own Deployment.

Listens for `order.created` and decrements product stock. Idempotent via the
ProcessedEvent ledger, so a redelivered event won't double-decrement.
"""
from __future__ import annotations

import logging
from typing import Any

from django.core.management.base import BaseCommand
from django.db.models import F

from catalog.consumers import run_consumer
from catalog.models import Product

logger = logging.getLogger(__name__)


def handle_order_created(payload: dict, _headers: dict) -> None:
    order_id = payload.get("order_id")
    for item in payload.get("items", []):
        sku_or_id = item["product_id"]
        qty = int(item["quantity"])
        # product_id in the event is the catalog SKU (stable cross-service id).
        updated = (
            Product.objects.filter(sku=sku_or_id, stock__gte=qty)
            .update(stock=F("stock") - qty)
        )
        if updated:
            logger.info("decremented %s by %s (order %s)", sku_or_id, qty, order_id)
        else:
            # Out of stock or unknown SKU — in a fuller build this would emit a
            # compensating event; for now we log it loudly.
            logger.warning("could not decrement %s by %s (order %s)", sku_or_id, qty, order_id)


class Command(BaseCommand):
    help = "Consume order.created and decrement stock."

    def handle(self, *args: Any, **opts: Any) -> None:
        run_consumer(
            group_id="catalog-consumer",
            handlers={"order.created": handle_order_created},
        )
