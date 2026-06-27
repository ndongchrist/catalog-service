"""DRF serializers for the catalog domain."""
from __future__ import annotations

from rest_framework import serializers

from .models import Product


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["id", "sku", "name", "description", "price", "stock"]
        read_only_fields = ["id"]
