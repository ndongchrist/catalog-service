from decimal import Decimal

import pytest

from catalog.management.commands.catalog_consumer import handle_order_created
from catalog.models import ProcessedEvent, Product


@pytest.fixture
def product(db):
    return Product.objects.create(sku="SKU-1", name="Thing", price=Decimal("9.99"), stock=10)


def test_list_products_is_public(api, product):
    resp = api.get("/products/")
    assert resp.status_code == 200
    assert resp.json()[0]["sku"] == "SKU-1"


def test_retrieve_product_by_sku(api, product):
    resp = api.get("/products/SKU-1/")
    assert resp.status_code == 200
    assert resp.json()["stock"] == 10


def test_create_product_requires_auth(api):
    resp = api.post("/products/", {"sku": "X", "name": "x", "price": "1.00", "stock": 1}, format="json")
    assert resp.status_code == 401


@pytest.mark.django_db
def test_create_product_with_gateway_user(api, auth_headers):
    resp = api.post(
        "/products/", {"sku": "NEW-1", "name": "New", "price": "5.00", "stock": 3},
        format="json", **auth_headers,
    )
    assert resp.status_code == 201
    assert Product.objects.filter(sku="NEW-1").exists()


@pytest.mark.django_db
def test_consumer_decrements_stock(product):
    event = {
        "event_id": "evt-1",
        "order_id": "ord-1",
        "items": [{"product_id": "SKU-1", "quantity": 3, "unit_price": "9.99"}],
    }
    handle_order_created(event, {})
    product.refresh_from_db()
    assert product.stock == 7


@pytest.mark.django_db
def test_consumer_does_not_oversell(product):
    handle_order_created(
        {"event_id": "e", "order_id": "o", "items": [{"product_id": "SKU-1", "quantity": 999}]}, {}
    )
    product.refresh_from_db()
    assert product.stock == 10  # unchanged: insufficient stock


@pytest.mark.django_db
def test_processed_event_ledger_dedupes(product):
    from catalog.consumers import _process_once

    event = {"event_id": "dup-1", "items": [{"product_id": "SKU-1", "quantity": 2}]}
    _process_once("order.created", "dup-1", event, {}, handle_order_created)
    _process_once("order.created", "dup-1", event, {}, handle_order_created)  # duplicate
    product.refresh_from_db()
    assert product.stock == 8  # decremented once, not twice
    assert ProcessedEvent.objects.filter(event_id="dup-1").count() == 1
