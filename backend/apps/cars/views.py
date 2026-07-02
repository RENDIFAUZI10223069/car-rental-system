from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from apps.common.cache_mixins import RedisCachedListMixin

from .models import Car
from .serializers import CarSerializer


class CarViewSet(RedisCachedListMixin, viewsets.ModelViewSet):
    """
    CRUD Data Mobil.

    - List/Retrieve -> dibaca dari PostgreSQL Replica (via db router), di-cache di Redis.
    - Create/Update/Delete -> ditulis ke PostgreSQL Primary, lalu invalidate cache.
    """
    serializer_class = CarSerializer
    permission_classes = [IsAuthenticated]
    cache_key_prefix = "cars"
    filterset_fields = ["status", "merk"]
    search_fields = ["plat_nomor", "merk", "model_mobil"]

    def get_queryset(self):
        return Car.objects.all()
