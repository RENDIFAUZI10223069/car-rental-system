from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from apps.common.cache_mixins import RedisCachedListMixin

from .models import Driver
from .serializers import DriverSerializer


class DriverViewSet(RedisCachedListMixin, viewsets.ModelViewSet):
    """
    CRUD Data Driver.
    List/Retrieve dari Replica + Redis cache. Write ke Primary.
    """
    serializer_class = DriverSerializer
    permission_classes = [IsAuthenticated]
    cache_key_prefix = "drivers"
    filterset_fields = ["status"]
    search_fields = ["nama_lengkap", "no_sim"]

    def get_queryset(self):
        return Driver.objects.all()
