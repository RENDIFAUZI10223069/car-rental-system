from datetime import date

from django.core.cache import cache
from django.db import transaction
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.cars.models import Car
from apps.drivers.models import Driver

from .models import Rental
from .serializers import (
    RentalCreateSerializer,
    RentalListSerializer,
    RentalReturnSerializer,
)

CACHE_PREFIX = "rentals"
DENDA_MULTIPLIER = 1.5  # tarif denda keterlambatan = 1.5x harga sewa harian per hari telat


def _invalidate_rentals_cache():
    try:
        cache.delete_pattern(f"{CACHE_PREFIX}:*")
    except AttributeError:
        cache.clear()


class RentalViewSet(viewsets.ModelViewSet):
    """
    Transaksi Rental Mobil.

    - create        -> POST /api/v1/rentals/            (tulis ke Primary)
    - return_car     -> POST /api/v1/rentals/{id}/return/ (tulis ke Primary)
    - list/history  -> GET  /api/v1/rentals/ | /api/v1/rentals/history/ (baca dari Replica + Redis cache)
    """
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "post", "head", "options"]

    def get_queryset(self):
        return Rental.objects.select_related("customer", "car", "driver").all()

    def get_serializer_class(self):
        if self.action == "create":
            return RentalCreateSerializer
        if self.action == "return_car":
            return RentalReturnSerializer
        return RentalListSerializer

    # ---------------------------------------------------------------
    # LIST & HISTORY -> selalu dari Replica (otomatis via DB Router) + Redis Cache
    # ---------------------------------------------------------------
    def list(self, request, *args, **kwargs):
        cache_key = f"{CACHE_PREFIX}:list:{request.query_params.urlencode()}"
        cached = cache.get(cache_key)
        if cached is not None:
            cached["_source"] = "redis-cache"
            return Response(cached)

        response = super().list(request, *args, **kwargs)
        cache.set(cache_key, response.data)
        response.data["_source"] = "postgresql-replica"
        return response

    @action(detail=False, methods=["get"], url_path="history")
    def history(self, request):
        """Endpoint khusus riwayat transaksi (read-only, dari Replica)."""
        return self.list(request)

    # ---------------------------------------------------------------
    # CREATE TRANSAKSI -> selalu ke Primary
    # ---------------------------------------------------------------
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        with transaction.atomic(using="default"):
            # Ambil ulang dari Primary (bukan Replica) untuk menghindari race-condition
            # akibat replication lag, lalu kunci baris (select_for_update).
            car = Car.objects.using("default").select_for_update().get(pk=data["car"].pk)
            if car.status != Car.Status.TERSEDIA:
                return Response(
                    {"detail": "Mobil sudah tidak tersedia."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            driver = data.get("driver")
            if driver is not None:
                driver = Driver.objects.using("default").select_for_update().get(pk=driver.pk)
                if driver.status != Driver.Status.TERSEDIA:
                    return Response(
                        {"detail": "Driver sudah tidak tersedia."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            durasi_hari = (data["tanggal_rencana_selesai"] - data["tanggal_mulai"]).days
            durasi_hari = max(durasi_hari, 1)
            total_biaya = durasi_hari * car.harga_sewa_harian

            rental = Rental.objects.create(
                customer=data["customer"],
                car=car,
                driver=driver,
                tanggal_mulai=data["tanggal_mulai"],
                tanggal_rencana_selesai=data["tanggal_rencana_selesai"],
                harga_sewa_harian_snapshot=car.harga_sewa_harian,
                total_biaya=total_biaya,
                catatan=data.get("catatan", ""),
                status=Rental.Status.BERJALAN,
            )

            car.status = Car.Status.DISEWA
            car.save(using="default")

            if driver is not None:
                driver.status = Driver.Status.BERTUGAS
                driver.save(using="default")

        _invalidate_rentals_cache()
        try:
            cache.delete_pattern("cars:*")
            cache.delete_pattern("drivers:*")
        except AttributeError:
            pass

        output = RentalListSerializer(rental, context=self.get_serializer_context())
        return Response(output.data, status=status.HTTP_201_CREATED)

    # ---------------------------------------------------------------
    # RETURN MOBIL -> selalu ke Primary
    # ---------------------------------------------------------------
    @action(detail=True, methods=["post"], url_path="return")
    def return_car(self, request, pk=None):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        with transaction.atomic(using="default"):
            rental = Rental.objects.using("default").select_for_update().select_related(
                "car", "driver"
            ).get(pk=pk)

            if rental.status == Rental.Status.SELESAI:
                return Response(
                    {"detail": "Transaksi ini sudah selesai / mobil sudah dikembalikan."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            tanggal_kembali = data.get("tanggal_kembali_aktual") or date.today()
            rental.tanggal_kembali_aktual = tanggal_kembali

            hari_telat = (tanggal_kembali - rental.tanggal_rencana_selesai).days
            if hari_telat > 0:
                denda = hari_telat * float(rental.harga_sewa_harian_snapshot) * DENDA_MULTIPLIER
                rental.denda_keterlambatan = denda
                rental.total_biaya = float(rental.total_biaya) + denda

            if data.get("catatan"):
                rental.catatan = data["catatan"]

            rental.status = Rental.Status.SELESAI
            rental.save(using="default")

            car = Car.objects.using("default").select_for_update().get(pk=rental.car_id)
            car.status = Car.Status.TERSEDIA
            car.save(using="default")

            if rental.driver_id:
                driver = Driver.objects.using("default").select_for_update().get(pk=rental.driver_id)
                driver.status = Driver.Status.TERSEDIA
                driver.save(using="default")

        _invalidate_rentals_cache()
        try:
            cache.delete_pattern("cars:*")
            cache.delete_pattern("drivers:*")
        except AttributeError:
            pass

        output = RentalListSerializer(rental, context=self.get_serializer_context())
        return Response(output.data, status=status.HTTP_200_OK)
