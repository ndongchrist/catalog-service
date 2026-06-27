"""Catalog API.

Browsing (list/retrieve) is public — catalog is the storefront. Other services
(cart, order) read stock via GET /products/{sku}/ over ClusterIP DNS. Creating
products requires an authenticated (admin) caller.
"""
from __future__ import annotations

from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated

from .models import Product
from .serializers import ProductSerializer


class ProductList(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get_permissions(self):
        # Public browse; authenticated create.
        return [AllowAny()] if self.request.method == "GET" else [IsAuthenticated()]


class ProductDetail(generics.RetrieveUpdateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    lookup_field = "sku"

    def get_permissions(self):
        return [AllowAny()] if self.request.method == "GET" else [IsAuthenticated()]
