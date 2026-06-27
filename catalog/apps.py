from django.apps import AppConfig


class CatalogConfig(AppConfig):
    name = "catalog"
    # Distinct label so a service named after a Django builtin (e.g. "auth")
    # doesn't collide with django.contrib.* app labels.
    label = "catalog_app"
