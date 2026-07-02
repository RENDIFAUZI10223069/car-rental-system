from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from apps.common.cache_mixins import RedisCachedListMixin

from .models import Customer
from .serializers import CustomerSerializer


class CustomerViewSet(RedisCachedListMixin, viewsets.ModelViewSet):
    """
    CRUD Data Pelanggan.
    List/Retrieve dari Replica + Redis cache. Write ke Primary.
    """
    serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticated]
    cache_key_prefix = "customers"
    search_fields = ["nama_lengkap", "no_ktp", "no_telepon"]

    def get_queryset(self):
        return Customer.objects.all()
